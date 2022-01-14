ARG PYTHON3_IMAGE=python:3.8-slim
ARG CHROMIUM_INSTALL_DIR=/opt/chromium


FROM node:14.18.2-alpine as minimal-chromium
ARG PUPPETEER_CHROMIUM_DIR=node_modules/puppeteer/.local-chromium/linux-*
ARG CHROMIUM_INSTALL_DIR

WORKDIR /src

RUN npm install puppeteer@13.0.1 --no-sandbox --no-optional --only=prod \
    && cd $PUPPETEER_CHROMIUM_DIR/chrome-linux \
    # remove 40MB of useless translation files
    && rm -rf locales \
    # delete 20MB of resources for the inspector tools
    # seems safe to delete, but resources.pak must be kept otherwise the HTML render is corrupted
    && rm -rf resources \
    # delete 40MB of other files that are not required in headless mode
    && chromeFilesSafeToDelete='libEGL.so nacl_helper nacl_helper_bootstrap ClearKeyCdm chrome_sandbox libGLESv2.so MEIPreload nacl_helper_nonsfi nacl_irt_x86_64.nexe' \
    && rm -rf $chromeFilesSafeToDelete \
    && mv chrome chromium \
    # move chromium to install dir
    && cd .. \
    && mv chrome-linux chromium \
    && mv chromium $CHROMIUM_INSTALL_DIR

FROM $PYTHON3_IMAGE as runtime
ARG CHROMIUM_INSTALL_DIR

# install Chromium dependencies
RUN apt-get update \
    # minimal list of dependencies to run chromium in headless mode,
    # might need to be adapted depending on the base image you use via PYTHON3_IMAGE
    && ubuntuDependencies='libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libcups2 libxss1 libxrandr2 libasound2 libatk1.0-0 libatk-bridge2.0-0 libpangocairo-1.0-0 libgtk-3-0 libdrm2 libgbm-dev' \
    && debianSlimDependencies='libnss3' \
    && apt-get -y install $ubuntuDependencies $debianSlimDependencies --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY --from=minimal-chromium $CHROMIUM_INSTALL_DIR $CHROMIUM_INSTALL_DIR
RUN ln -s $CHROMIUM_INSTALL_DIR/chromium /usr/bin/chromium

WORKDIR /src

COPY requirements.txt requirements.txt
RUN apt-get update \
    && devDependencies='procps git' \
    && apt-get install -qqy $devDependencies --no-install-recommends \
    && pip3 install -r requirements.txt

