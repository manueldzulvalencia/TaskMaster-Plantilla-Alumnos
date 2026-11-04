#!/usr/bin/env bash
set -euo pipefail

export ANDROID_HOME="${ANDROID_HOME:-$HOME/android-sdk}"
export ANDROID_SDK_ROOT="$ANDROID_HOME"

mkdir -p "$ANDROID_HOME/cmdline-tools"

if [ ! -x "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" ]; then
    echo "Descargando herramientas oficiales de Android..."
    curl -fL --retry 3 \
      "https://dl.google.com/android/repository/commandlinetools-linux-13114758_latest.zip" \
      -o /tmp/android-commandline-tools.zip

    mkdir -p /tmp/android-commandline-extract
    unzip -q /tmp/android-commandline-tools.zip \
      -d /tmp/android-commandline-extract

    mv /tmp/android-commandline-extract/cmdline-tools \
      "$ANDROID_HOME/cmdline-tools/latest"
fi

echo "Instalando componentes del SDK..."

set +o pipefail
yes | "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" \
    --sdk_root="$ANDROID_HOME" --licenses
resultado=${PIPESTATUS[1]}
set -o pipefail

if [ "$resultado" -ne 0 ]; then
    echo "ERROR: No se pudieron aceptar las licencias del SDK."
    exit "$resultado"
fi

"$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" \
    --sdk_root="$ANDROID_HOME" \
    "platform-tools" \
    "platforms;android-37.0" \
    "build-tools;36.0.0"

echo "SDK de Android instalado correctamente."
