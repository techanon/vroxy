#!/bin/bash

echo This script will automatically setup all dependencies and an NGINX server with a LetsEncrypt SSL cert.

if [[ `whoami` != root ]]; then
    echo Permission escalation required. Please run this script as root or using sudo.
    exit
fi

echo '>>> Some information is needed from you <<<'
read -p "Please select the folder for Vroxy to install into or update in (default is /var/vroxy): " dir

if [ ! $dir ]; then dir='/var/vroxy'; fi
if [[ -f "$dir/settings.ini" ]]; then
    defaultdomain=$(grep -E "domain=" $dir/settings.ini | cut -d'=' -f2)
    defaultport=$(grep -E "port=" $dir/settings.ini | cut -d'=' -f2)
fi

if [ ! $defaultport ]; then defaultport=8420; fi
if [ $defaultdomain ]; then
    domainmsg = "(leave empty for $defaltdomain)"
else
    domainmsg = "(required)"
fi


read -p "Please enter the domain name you wish to setup with the NGINX configuration ($domainmsg): " domain
read -p "Please specify what port to run the Vroxy service on (leave empty for $defaultport): " port

if [ ! $port ]; then port=defaultport; fi
if [ ! $domain ]; then
    if [ ! $defaultdomain ]; then
        echo "No domain name provided. This is required information for initial setup. Rerun script and specify the domain name."
        exit 1
    else
        domain=defaultdomain
    fi
fi

echo "Domain: $domain | Reverse Proxy Port: $port | Vroxy Location: $dir"

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
if [ $domain ]; then
echo ---
echo Configuring NGINX with LetsEncrypt SSL Certs
echo ---
cat << EOF > /etc/nginx/conf.d/$domain.conf
server {
    server_name $domain;
    location / {
        proxy_pass http://localhost:$port;
    }
}
EOF
echo NGINX Configuration stored in /etc/nginx/conf.d/$domain.conf
nginx -t && nginx -s reload

echo ---
echo Setting up LetsEncrypt
echo ---

certbot -n --nginx --redirect --no-eff-email --agree-tos --register-unsafely-without-email -d $domain
if crontab -l | grep -Fxq '0 12 * * * /usr/bin/certbot renew --quiet'; then
    echo LetsEncrypt Autorenew cron found. Skipping.
else
    (crontab -l ; echo "
    # Lets Encrypt SSL Autorenew
    0 12 * * * /usr/bin/certbot renew --quiet
    0 3 * * * bash $dir/reload.sh
    ") | crontab -
    echo LetsEncrypt Autorenew and Vroxy service auto-reload crons added.
fi
echo ---
echo "Setting up Vroxy in $dir"
echo ---
mkdir $dir
if [ $SUDO_USER ]; then
    # enforce calling user has ownership of the directory and files
    chown -R $SUDO_USER $dir
fi
cd $dir
if [[ ! -d "$dir/.git" ]]; then
    git clone https://github.com/techanon/vroxy.git $dir
    git config pull.ff only
    git config --global --add safe.directory $dir
else
    # if it already exists, just grab the latest instead
    git pull
fi
cat << EOF > settings.ini
[server]
domain=$domain
host=localhost
port=$port
EOF
python3 -m pip install -U yt-dlp aiohttp
if [ $SUDO_USER ]; then
    # re-enforce calling user has ownership of the directory and files
    chown -R $SUDO_USER $dir
    su $SUDO_USER -c "bash $dir/reload.sh"
else
    # is actually just root user, no sudo being used, all good
    bash $dir/reload.sh
fi
echo ---
echo "Vroxy service is now running on https://$domain/ from $dir"
echo "Try it out with this sample URL: https://$domain/?url=https://www.youtube.com/watch?v=wpV-gGA4PSk"
echo "If you need to restart or update the service, run this command: bash $dir/reload.sh"
echo "You can view the Vroxy logs via 'tmux a -t vroxy'."
echo "In the tmux session you can cleanly exit via CTRL+B and the clicking the D key."
echo ---