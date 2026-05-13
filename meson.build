project('bootqt',
          version: 'v2026.5.13',
    meson_version: '>= 0.61.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())

configure_file(
  input: 'data/bootqt-launch.sh.in',
  output: 'bootqt-launch.sh',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x',
)

install_data('bootqt.py', install_dir: '/app/lib/bootqt')

install_data(
  'data/bqlogo.png',
  install_dir: '/app/share/icons/hicolor/256x256/apps',
  rename: 'io.github.giantpinkrobots.bootqt.png'
)

install_data(
  'data/bqlogo.png',
  install_dir: '/app/lib/bootqt',
  rename: 'io.github.giantpinkrobots.bootqt.png'
)

install_data(
  'data/io.github.giantpinkrobots.bootqt.desktop',
  install_dir: '/app/share/applications'
)

install_data(
  'flatpak/io.github.giantpinkrobots.bootqt.metainfo.xml',
  install_dir: '/app/share/metainfo'
)

install_subdir(
  'bqi18n',
  install_dir: '/app/lib/bootqt'
)