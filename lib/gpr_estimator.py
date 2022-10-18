import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow.compat.v2 as tf
import tensorflow_probability as tfp

tf.get_logger().setLevel('INFO')

tfb = tfp.bijectors
tfd = tfp.distributions
tfk = tfp.math.psd_kernels
tf.enable_v2_behavior()


def array_chunker(arr_, size=1000):
    check_size = True
    while check_size:
        size_now = arr_.shape[0]
        # print(size_now)
        if size_now < size:
            check_size = False
            yield arr_
        else:
            chunk = arr_[:size,...]
            arr_ = arr_[size:,...]
            yield chunk


class GPREstimator:
    def __init__(self, pandas_obj, **kwargs) -> None:
        '''
        Prepare arguments for optimization
        '''
        self._obj = pandas_obj
        self.parse_estimation(**kwargs)
        self.gp_joint_model = tfd.JointDistributionNamed({
            'amplitude': tfd.LogNormal(
                loc=0., scale=np.float64(1.)
            ),
            'length_scale': tfd.LogNormal(
                loc=0., scale=np.float64(1.)
            ),
            'observation_noise_variance': tfd.LogNormal(
                loc=0., scale=np.float64(1.)
            ),
            'observations': (
                lambda 
                amplitude, length_scale, observation_noise_variance: 
                self.build_gp(
                    amplitude=amplitude,
                    length_scale=length_scale,
                    observation_noise_variance=observation_noise_variance
                )
            )
        })

        # Create the trainable model parameters, 
        # which we'll subsequently optimize.
        # Note that we constrain them to be strictly positive.
        self.constrain_positive = tfb.Shift(
            np.finfo(np.float64).tiny
        )(tfb.Exp())

        self.amplitude_var = tfp.util.TransformedVariable(
            initial_value=1.,
            bijector=self.constrain_positive,
            name='amplitude',
            dtype=np.float64
        )

        self.length_scale_var = tfp.util.TransformedVariable(
            initial_value=1.,
            bijector=self.constrain_positive,
            name='length_scale',
            dtype=np.float64
        )

        self.observation_noise_variance_var = (
            tfp.util.TransformedVariable(
                initial_value=1.,
                bijector=self.constrain_positive,
                name='observation_noise_variance_var',
                dtype=np.float64
            )
        )

        self.trainable_variables = [
            v.trainable_variables[0] 
            for v in [
                self.amplitude_var, 
                self.length_scale_var, 
                self.observation_noise_variance_var
            ]
        ]
    
    def parse_estimation(
        self, 
        obs_index=['vl_longitude', 'vl_latitude', 'vl_altitude'], 
        obs='year_mean'
    ):
        self.observation_indices_ = (
            self._obj.reset_index()[obs_index].to_numpy()
        )
        self.observations_ = self._obj[obs].to_numpy()

        self.index_names = obs_index
        self.var_name = obs

    def build_gp(
        self, amplitude, length_scale, observation_noise_variance
        ):
        """
        Defines the conditional dist. of GP outputs, 
        given kernel parameters.
        """
        # Create the covariance kernel, 
        # which will be shared between the prior 
        # (which we use for maximum likelihood training) 
        # and the posterior 
        # (which we use for posterior predictive sampling)
        kernel = tfk.ExponentiatedQuadratic(amplitude, length_scale)

        # Create the GP prior distribution, 
        # which we will use to train the model parameters.
        return tfd.GaussianProcess(
            kernel=kernel,
            index_points=self.observation_indices_,
            observation_noise_variance=observation_noise_variance)

    @tf.function(autograph=False, experimental_compile=False)
    def target_log_prob(
        self, 
        amplitude, 
        length_scale, 
        observation_noise_variance
    ):
        return self.gp_joint_model.log_prob({
            'amplitude': amplitude,
            'length_scale': length_scale,
            'observation_noise_variance': observation_noise_variance,
            'observations': self.observations_
        })

    def optimize(
        self,
        num_iters=10000, 
        optimizer=tf.optimizers.Adam(learning_rate=.01)
    ):

        # Store the likelihood values during training, 
        # so we can plot the progress
        lls_ = np.zeros(num_iters, np.float64)
        for i in range(num_iters):
            with tf.GradientTape() as tape:
                loss = -self.target_log_prob(
                    self.amplitude_var, 
                    self.length_scale_var,
                    self.observation_noise_variance_var
                )
            grads = tape.gradient(loss, self.trainable_variables)
            optimizer.apply_gradients(zip(grads, self.trainable_variables))
            lls_[i] = loss

        self.log_lik = lls_

    def plot_loglik(self):
        x = range(self.log_lik.shape[0])
        plt.ylabel('Log likelihood')
        plt.xlabel('Iteration')
        plt.plot(x, self.log_lik)
        plt.show()

    def print_parameters(self):
        print('Trained parameters:')
        print(f'amplitude: {self.amplitude_var._value().numpy()}')
        print(f'length_scale: {self.length_scale_var._value().numpy()}')
        print(
            f'observation_noise_variance: '
            f'{self.observation_noise_variance_var._value().numpy()}'
        )

    def predict(self, predictive_indices_):
        self.optimized_kernel = tfk.ExponentiatedQuadratic(
            self.amplitude_var, 
            self.length_scale_var
        )

        collector = []

        # num_samples = 100

        gprm_static = tfd.GaussianProcessRegressionModel(
            kernel=self.optimized_kernel,
            observation_index_points=self.observation_indices_,
            observations=self.observations_,
            observation_noise_variance=self.observation_noise_variance_var,
            predictive_noise_variance=0.
        )

        chunks = array_chunker(predictive_indices_, size=100)

        for chunk in chunks:
            # Create op to draw __size__ independent samples, 
            # each of which is a *joint* draw from the posterior 
            # at the predictive_indices_. Since we have __size__ input
            # locations as defined above, this posterior distribution 
            # over corresponding function values is a 
            # size-dimensional multivariate Gaussian distribution
            sampler = gprm_static.get_marginal_distribution(chunk)
            means = sampler.mean()
            sdevs = sampler.stddev()

            _pd = pd.DataFrame(chunk, columns=self.index_names)
            _pd[f'{self.var_name}_estimate'] = means
            _pd[f'{self.var_name}_sdev'] = sdevs
            collector.append(_pd)

        self.estimates = pd.concat(collector)
