### Certbot setup with Apache on Ubuntu16.04(xenial)

1. add Certbot PPA
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update

2. Install Certbot
sudo apt-get install certbot python-certbot-apache

3. Get and install certificates
sudo certbot --apache

4. Test automatic renewal 
sudo certbot renew --dry-run

Note: I didn't switch to https exclusively, both exists. Should change it.

[reference](https://certbot.eff.org/lets-encrypt/ubuntuxenial-apache)
