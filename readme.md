Certifique-se de que os dados estão sendo indexados corretamente: Parece que você pode ter um problema com a forma como as datas estão sendo manuseadas no DataFrame price_data. Se o índice estiver realmente começando em 1970, isso sugere que as datas podem estar em um formato de timestamp incorreto ou não foram convertidas corretamente para o tipo de dado datetime.

Verificar a preparação dos dados: No método \_prepare_data da classe YahooFinanceFetcher, você converte a coluna 'ds' para datetime. Verifique se esta conversão está funcionando corretamente e se o índice resultante tem as datas esperadas.

Consertar os índices do hilo_long e hilo_short: Assegure-se de que o hilo_long e hilo_short são convertidos para Series com índices que correspondem ao índice price_data. Se houver qualquer diferença nos índices, a comparação entre eles falhará. Você está convertendo para Series com o índice de price_data, o que está correto, mas verifique se o índice de price_data está definido corretamente antes disso.

KLBN11
CRFB3
