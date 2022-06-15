#!/usr/bin/env bash

echo This script will automatically setup NGINX with LetsEncrypt SSL.

if [[ `whoami` != root ]]; then
    echo Permission escalation required. Please run this script as root or using sudo.
    exit
fi

echo '>>> Some information is needed from you <<<'
read -p "Please select the folder to install Qroxy into (default is /var/qroxy): " floc
read -p "Please enter the domain name you wish to setup with the NGINX configuration: " dname
read -p "Please specify what port to run the Qroxy service on (defaults to 8008): " port
if [ ! $floc ]; then
    floc='/var/qroxy'
fi
if [ ! $port ]; then
    port=8008
fi

echo "Domain: $dname | Reverse Proxy Port: $port | Qroxy Location: $floc"

cd ~
echo ---
echo Installing common dependencies
echo ---
apt install -y git software-properties-common tmux gpg gpg-agent dirmngr nginx certbot
echo ---
echo Installing python dependencies
echo ---
add-apt-repository -y ppa:deadsnakes/ppa
apt install -y python3.9 python3-pip python3-certbot-nginx
echo ---
echo Configuring NGINX with LetsEncrypt SSL Certs
echo ---
cat << EOF > /etc/nginx/conf.d/$dname.conf
server {
    server_name $dname;
    location / {
        proxy_pass http://localhost:$port;
    }
}
EOF
echo NGINX Configuration stored in /etc/nginx/conf.d/$dname.conf
nginx -t && nginx -s reload

echo ---
echo Setting up LetsEncrypt
echo ---

certbot -n --nginx --no-eff-email --agree-tos --register-unsafely-without-email -d $dname
if crontab -l | grep -Fxq '0 12 * * * /usr/bin/certbot renew --quiet'; then
    echo LetsEncrypt Autorenew cron found. Skipping.
else
    (crontab -l ; echo '
    # Lets Encrypt SSL Autorenew
    0 12 * * * /usr/bin/certbot renew --quiet
    ') | crontab -
    echo LetsEncrypt Autorenew cron added.
fi
echo ---
echo "Setting up Qroxy in $floc"
echo ---
mkdir $floc
if [[ ! -d "$floc/.git" ]]; then
    git clone https://github.com/techanon/qroxy.git $floc
    git config pull.ff only
    git config --global --add safe.directory $floc
else
    # if it already exists, just grab the latest instead
    git pull
fi
cd $floc
cat << EOF > settings.ini
[server]
host=localhost
port=$port
EOF
python3 -m pip install -U yt-dlp aiohttp
chown -R $SUDO_USER .
echo ---
echo "You may now test out the Qroxy service via 'cd $floc && python3 qroxy.py' and access it via https://$dname/"
echo "Try it out with this sample URL: https://$dname/?url=https://www.youtube.com/watch?v=wpV-gGA4PSk"
echo "It is recommended to use a tool like tmux to run the service without needing to be connected to the terminal"
echo "You can do so with this command: bash $floc/tmux_reboot.sh"