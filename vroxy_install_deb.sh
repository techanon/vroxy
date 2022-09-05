#!/bin/bash

set -e

echo This script will automatically setup all dependencies and an NGINX server with a LetsEncrypt SSL cert.

if [[ `whoami` != root ]]; then
    echo Permission escalation required. Please run this script as root or using sudo.
    exit
fi

is_interactive="1"
if [[ -n "$DEBIAN_FRONTEND" && "$DEBIAN_FRONTEND" == "noninteractive" ]]; then
    echo "Running in noninteractive mode"
    is_interactive="0"
fi

if [[ $is_interactive == "1" ]]; then
    echo '

    >>> Some information is needed from you <<<

    '
    read -p "Please select the folder for Vroxy to install into or update in (leave empty for /var/vroxy): " dir
fi

if [ ! $dir ]; then dir='/var/vroxy'; fi
if [[ -f "$dir/settings.ini" ]]; then
    defaultdomain=$(grep -E "domain=" $dir/settings.ini | cut -d'=' -f2)
    defaultport=$(grep -E "port=" $dir/settings.ini | cut -d'=' -f2)
fi

if [ ! $defaultport ]; then defaultport=8420; fi
domainmsg='required'
if [ $defaultdomain ]; then domainmsg="leave empty for $defaultdomain"; fi


if [[ $is_interactive == "1" ]]; then
    read -p "Please enter the domain name you wish to setup with the NGINX configuration ($domainmsg): " domain
    read -p "Please specify what port to run the Vroxy service on (leave empty for $defaultport): " port
fi

if [ ! $port ]; then port=$defaultport; fi
if [ ! $domain ]; then
    if [ ! $defaultdomain ]; then
        echo "No domain name provided. This is required information for initial setup. Rerun script and specify the domain name."
        exit 1
    else
        domain=$defaultdomain
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
echo ---
echo Configuring NGINX with LetsEncrypt SSL Certs
echo ---
cat << EOF > /etc/nginx/conf.d/$domain.conf
server {
    server_name $domain;
    location / {
        proxy_pass http://0.0.0.0:$port;
    }
    
    error_log /var/log/nginx/$domain.error.log;
    access_log /var/log/nginx/$domain.access.log;
}
EOF
echo NGINX Configuration stored in /etc/nginx/conf.d/$domain.conf

nginx -t
if [[ -s /run/nginx.pid ]]; then
    nginx -s reload
fi

echo ---
echo Setting up LetsEncrypt
echo ---

extra_cb_args=""

if [[ -n "$acme_server" ]]; then
    extra_cb_args="$extra_cb_args --server $acme_server"
fi

certbot \
    -n \
    --nginx \
    --redirect \
    --no-eff-email \
    --agree-tos \
    --register-unsafely-without-email \
    $extra_cb_args \
    -d $domain

if [[ -f /etc/cron.d/certbot ]]; then
    echo LetsEncrypt Autorenew cron found. Skipping.
else
    cat << 'EOF' > /etc/cron.d/certbot
# Lets Encrypt SSL Autorenew
0 12 * * * root /usr/bin/certbot renew --quiet
EOF
    echo LetsEncrypt Autorenew cron added.
fi

if [[ -f /etc/cron.d/vroxy ]]; then
    echo Vroxy service auto-reload cron found. Skipping.
else
    cat << 'EOF' > /etc/cron.d/vroxy
# Vroxy service auto-reload
0 3 * * * root bash $dir/vroxy_reload.sh
EOF
    echo Vroxy service auto-reload cron added.
fi

echo ---
echo "Setting up Vroxy in $dir"
echo ---
mkdir $dir
if [ ! $(git config --global --get-all safe.directory | grep "$dir") ]; then
    # ensure that git knows that this new directory is safe
    git config --global --add safe.directory $dir
fi
if [ $SUDO_USER ]; then
    # enforce calling user has ownership of the directory and files
    chown -R $SUDO_USER $dir
fi
cd $dir
if [[ ! -d "$dir/.git" ]]; then
    git clone https://github.com/techanon/vroxy.git $dir
    git config pull.ff only
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
python3 -m pip install -U yt-dlp aiohttp tldextract
if [ $SUDO_USER ]; then
    # re-enforce calling user has ownership of the directory and files
    chown -R $SUDO_USER $dir
    su $SUDO_USER -c "bash $dir/vroxy_reload.sh"
else
    # is actually just root user, no sudo being used, all good
    bash $dir/vroxy_reload.sh
fi
echo ---
echo "Vroxy service is now running on https://$domain/ from $dir"
echo "Try it out with this sample URL: https://$domain/?url=https://www.youtube.com/watch?v=wpV-gGA4PSk"
echo "If you need to restart or update the service, run this command: bash $dir/vroxy_reload.sh"
echo "You can view the Vroxy logs via 'tmux a -t vroxy'."
echo "In the tmux session you can cleanly exit via CTRL+B and the clicking the D key."
echo ---
