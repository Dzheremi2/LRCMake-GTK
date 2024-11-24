<div align="center">

# LRCMake
[flathub-url]: https://flathub.org/apps/io.github.dzheremi2.lrcmake-gtk
[installs-img]: https://img.shields.io/flathub/downloads/io.github.dzheremi2.lrcmake-gtk?style=for-the-badge&color=gree

![GitHub Release](https://img.shields.io/github/v/release/Dzheremi2/LRCMake-GTK?style=for-the-badge&color=000B3C)
[![Installs][installs-img]][flathub-url]
![GitHub License](https://img.shields.io/github/license/Dzheremi2/LRCMake-GTK?style=for-the-badge&color=C25D00)
![Weblate project translated](https://img.shields.io/weblate/progress/lrcmake?style=for-the-badge&logo=weblate&logoColor=white&logoSize=auto&color=magenta&cacheSeconds=600)

<img src="data/icons/hicolor/scalable/apps/io.github.dzheremi2.lrcmake-gtk.svg" width="150">

![Screenshot](docs/screenshots/lib.png)

</div>

### What is LRCMake
LRCMake is the app written in python using GTK4 and LibAdwaita. LRCMake is used for syncing lyrics for future contributing it to various resources, especially [LRCLIB](https://lrclib.net).

LRCMake support exporting lyrics to clipboard and direct publishing to [LRCLIB](https://lrclib.net).

### Installation
<a href='https://flathub.org/apps/io.github.dzheremi2.lrcmake-gtk'>
    <img width='240' alt='Get it on Flathub' src='https://flathub.org/api/badge?svg&locale=en'/>
</a>

You can download app either on [Flathub](https://flathub.org/apps/io.github.dzheremi2.lrcmake-gtk) or by downloading and installing bundle from [latest release](https://github.com/Dzheremi2/LRCMake-GTK/releases/latest)

### Translation
You can help project to be internationalized using [Hosted Weblate](https://hosted.weblate.org/projects/lrcmake/lrcmake/)

##### Translation status

[![Состояние перевода](https://hosted.weblate.org/widget/lrcmake/lrcmake/287x66-black.png)](https://hosted.weblate.org/engage/lrcmake/)
[![Translate state](https://hosted.weblate.org/widget/lrcmake/lrcmake/multi-auto.svg)](https://hosted.weblate.org/engage/lrcmake/)

### Plans
You can see future plans on Projects page of this repo on [LRCMake roadmap.](https://github.com/users/Dzheremi2/projects/2)

If you have an idea or you know a bug, please, open an issue with you idea/bug and it will be added to roadmap.

### Building

#### Dependencies
You'll need to install `flatpak-builder` package and `org.gnome.Platform` flatpak runtime of version `47`

#### Building

Execute this commands one-by-one:
*Replace ***{repofolder}*** with your path to repository directory*

```shell
flatpak build-init {repofolder}/.flatpak/repo io.github.dzheremi2.lrcmake-gtk org.gnome.Sdk org.gnome.Platform 47
```
```shell
flatpak-builder --ccache --force-clean --disable-updates --download-only --state-dir=/home/dzheremi/Projects/LRCMake/.flatpak/flatpak-builder --stop-at=python3-modules {repofolder}/.flatpak/repo {repofolder}/io.github.dzheremi2.lrcmake-gtk.json
```
```shell
flatpak-builder --ccache --force-clean --disable-updates --disable-download --build-only --keep-build-dirs --state-dir=/home/dzheremi/Projects/LRCMake/.flatpak/flatpak-builder --stop-at=python3-modules {repofolder}/.flatpak/repo {repofolder}/io.github.dzheremi2.lrcmake-gtk.json
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
flatpak build-bundle {repofolder}/.flatpak/ostree-repo io.github.dzheremi2.lrcmake-gtk.flatpak io.github.dzheremi2.lrcmake-gtk
```

### Screenshots

![](docs/screenshots/syncing.png)
![](docs/screenshots/file_info.png)
![](docs/screenshots/lib_light.png)
![](docs/screenshots/syncing_light.png)
![](docs/screenshots/file_info_light.png)