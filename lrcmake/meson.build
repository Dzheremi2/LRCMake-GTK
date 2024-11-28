pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'lrcmake'
gnome = import('gnome')

configure_file(
  input: 'lrcmake.in',
  output: 'lrcmake',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)
install_subdir('components', install_dir: moduledir)
install_subdir('methods', install_dir: moduledir)
install_data(
    [
    'main.py',
    'window.py',
    configure_file(input: 'shared.py.in', output: 'shared.py', configuration: conf),
  ],
  install_dir: moduledir,
)
