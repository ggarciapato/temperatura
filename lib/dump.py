    # af_xpath= '/html/body/div[1]/div/div/ul/li[1]/a/span'
    # abrir_fechar = (
    #     WebDriverWait(driver, TIMEOUT)
    #     .until(EC.element_to_be_clickable((By.XPATH, af_xpath)))
    # )
    # abrir_fechar.click()
    
    driver.save_screenshot('abriu.png')

    # produto_xpath = '/html/body/div[1]/div/div/ul/li[1]/nav/div/ul/li[2]/select'
    produto = (
        WebDriverWait(driver, TIMEOUT)
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.produto')))
    )
    produto_select = Select(produto)

    # print([opt.text for opt in produto_select.options])

    produto_select.select_by_value('TabelaEstacoes')
    
    # tipo_xpath = '/html/body/div[1]/div/div/ul/li[1]/nav/div/ul/div[9]/li[1]/select'
    tipo_css = '#menu_EstacoesTabela > li:nth-child(1) > select:nth-child(2)'
    tipo = (
        WebDriverWait(driver, TIMEOUT)
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR, tipo_css)))
    )
    tipo_select = Select(produto)
    tipo_select.select_by_value(
        'T' if 'A' in estacao or 'B' in estacao else 'M'
    )

    # estacao_xpath = '/html/body/div[1]/div/div/ul/li[1]/nav/div/ul/div[9]/li[2]/select'  
    estacao_css = '#menu_EstacoesTabela > li:nth-child(2) > select:nth-child(2)'
    _est = (
        WebDriverWait(driver, TIMEOUT)
        .until(EC.element_to_be_clickable((By.XPATH, estacao_css)))
    )
    estacao_select = Select(produto)
    estacao_select.select_by_value(estacao)

