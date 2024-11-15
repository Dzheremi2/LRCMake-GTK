# LRCMake

![GitHub Release](https://img.shields.io/github/v/release/Dzheremi2/LRCMake-GTK)
![GitHub License](https://img.shields.io/github/license/Dzheremi2/LRCMake-GTK)


![Screenshot](docs/screenshots/lib.png)

### What is LRCMake
LRCMake is the app written in python using GTK4 and LibAdwaita. LRCMake is used for syncing lyrics for future contributing it to various resources, especially [LRCLIB](https://lrclib.net).

LRCMake support exporting lyrics to clipboard and direct publishing to [LRCLIB](https://lrclib.net).

### Installation

Download `.flatpak` file from the [latest release](https://github.com/Dzheremi2/LRCMake-GTK/releases/latest) and install it.

### Building

#### Dependencies
You'll need to install `flatpak-builder` package and `org.gnome.Platform` flatpak runtime of version `47`

#### Building

Execute this commands one-by-one:
*Replace ***{repofolder}*** with your path to repository directory*

```shell
flatpak build-init {repofolder}/.flatpak/repo com.github.dzheremi.lrcmake org.gnome.Sdk org.gnome.Platform 47
```
```shell
flatpak-builder --ccache --force-clean --disable-updates --download-only --state-dir=/home/dzheremi/Projects/LRCMake/.flatpak/flatpak-builder --stop-at=python3-modules {repofolder}/.flatpak/repo {repofolder}/com.github.dzheremi.lrcmake.json
```
```shell
flatpak-builder --ccache --force-clean --disable-updates --disable-download --build-only --keep-build-dirs --state-dir=/home/dzheremi/Projects/LRCMake/.flatpak/flatpak-builder --stop-at=python3-modules {repofolder}/.flatpak/repo {repofolder}/com.github.dzheremi.lrcmake.json
```
```shell
cp -r {repofolder}/.flatpak/repo {repofolder}/.flatpak/finalized-repo
```
```shell
flatpak build-finish --share=network --share=ipc --socket=fallback-x11 --device=dri --socket=wayland --socket=pulseaudio --command=lrcmake {repofolder}/.flatpak/finalized-repo
```
```shell
flatpak build-export {repofolder}/.flatpak/ostree-repo {repofolder}/.flatpak/finalized-repo
```
```shell
flatpak build-bundle {repofolder}/.flatpak/ostree-repo com.github.dzheremi.lrcmake.flatpak com.github.dzheremi.lrcmake
```

### Screenshots

![](docs/screenshots/syncing.png)
![](docs/screenshots/file_info.png)