# autocheckout-prestashop
Script python que permet comprar semi-automàticament items en una botiga prestashop.

Son necessàries les cookies d'usuari (amb mètode de pagament i direcció configurada) ja que en prestashop només és pot comprar un cop registrat. Aquestes es poden extreure amb extensions de chrome com EditThisCookie.

S'introdueixen les cookies, el codi del item (que es pot trobar a la url) i la quantitat que és vol. Si no està disponible s’anirà comprovant periòdicament la disponibilitat fins que torni a estar en stock. Un cop disponible s'afegeix al carro de la compra i es guarda l’enllaç a la passarel·la de pagament en un arxiu HTML.
