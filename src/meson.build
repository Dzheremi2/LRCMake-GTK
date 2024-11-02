pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'lrcmake'
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'gtk/window.blp',
    'gtk/components/noDirSelectedGreeting.blp',
    'gtk/components/songCard.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('lrcmake',
  'lrcmake.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'lrcmake.in',
  output: 'lrcmake',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

lrcmake_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'components/noDirSelectedGreeting.py',
  'methods/selectData.py',
]

install_data(lrcmake_sources, install_dir: moduledir)
