pkgname=cosmic-mixer
pkgver=0.1.0
pkgrel=1
pkgdesc="Cosmic Mixer – lightweight PipeWire/PulseAudio mixer for Linux"
arch=('any')
url="https://github.com/elementare/CosmicMixer"
license=('MIT')

depends=('python' 'python-pyqt6')
makedepends=('python-build' 'python-installer' 'python-pip')

source=("CosmicMixer::git+https://github.com/elementare/CosmicMixer.git")
sha256sums=('SKIP')

build() {
  cd CosmicMixer
  python -m build --wheel --no-isolation
}

package() {
  cd CosmicMixer
  python -m installer --destdir="$pkgdir" dist/*.whl
}