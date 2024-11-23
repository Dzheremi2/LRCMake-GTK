project('lrcmake',
          version: '0.1.2 (4c95c8f)',
    meson_version: '>= 1.0.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

i18n = import('i18n')
gnome = import('gnome')
python = import('python')

py_installation = python.find_installation('python3')

app_id = 'io.github.dzheremi2.lrcmake-gtk'
prefix = '/io/github/dzheremi2/lrcmake-gtk'
python = import('python')
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('APP_ID', app_id)
conf.set('PREFIX', prefix)
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix') / get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

subdir('data')
subdir('src')
subdir('po')

gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)
