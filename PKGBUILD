pkgname=blackhole-sim pkgver=1.0 pkgrel=1 pkgdesc="A terminal-based black hole orbital simulator with dynamic star orbits" arch=('any') url="https://github.com/bactaholic/blackhole-sim" depends=('python') source=('black_hole_simulator.py') md5sums=('SKIP')

package() { install -Dm755 "$srcdir/src/blackhole_sim.py" "$pkgdir/usr/bin/blackhole" }