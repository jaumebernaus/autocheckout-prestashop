# autocheckout-prestashop
Script python que permet comprar semi-automaticament items en una botiga prestashop.

Son necessaries les cookies d'usuari (amb metodé de pagament i direcció configurada) ja que en prestashop només és pot comprar un cop registrat. Aquestes es poden extreure amb alguna extensió de chrome com EditThisCookie.

S'introdueixen les cookies, el codi del item que es pot trobar a la url i la quantitat que és vol del producte. Si no està disponible anira monitorejant a que el producte estigui en stock. Un cop disponible s'afegeix al cart i és crea un archiu que amb un botó ens porta la pasarel·la de pagament. 
