"""Serveur statique de developpement, avec en-tetes Range.

Le serveur integre de Python (`http.server`) ignore l'en-tete `Range` : Chrome
declare alors la video non deplacable (`seekable` vide) et tout `currentTime`
retombe a 0. Ce module ajoute le strict necessaire pour que le seek fonctionne
en local comme il fonctionnera sur l'hebergement.
"""

import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4173
RANGE = re.compile(r"bytes=(\d*)-(\d*)")


class RangeHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-store")
        SimpleHTTPRequestHandler.end_headers(self)

    def send_head(self):
        entete = self.headers.get("Range")
        if not entete:
            return SimpleHTTPRequestHandler.send_head(self)

        correspondance = RANGE.match(entete)
        chemin = self.translate_path(self.path)
        if not correspondance or os.path.isdir(chemin):
            return SimpleHTTPRequestHandler.send_head(self)

        try:
            fichier = open(chemin, "rb")
        except OSError:
            self.send_error(404)
            return None

        taille = os.fstat(fichier.fileno()).st_size
        debut, fin = correspondance.group(1), correspondance.group(2)
        if debut == "":                      # bytes=-N : les N derniers octets
            debut = max(0, taille - int(fin))
            fin = taille - 1
        else:
            debut = int(debut)
            fin = int(fin) if fin else taille - 1
        fin = min(fin, taille - 1)

        if debut > fin:
            fichier.close()
            self.send_response(416)
            self.send_header("Content-Range", "bytes */%d" % taille)
            self.end_headers()
            return None

        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(chemin))
        self.send_header("Content-Range", "bytes %d-%d/%d" % (debut, fin, taille))
        self.send_header("Content-Length", str(fin - debut + 1))
        self.end_headers()
        fichier.seek(debut)
        return _Tranche(fichier, fin - debut + 1)


class _Tranche:
    """Lecture limitee a la tranche demandee, pour `copyfile`."""

    def __init__(self, fichier, reste):
        self.fichier = fichier
        self.reste = reste

    def read(self, taille=-1):
        if self.reste <= 0:
            return b""
        if taille < 0 or taille > self.reste:
            taille = self.reste
        bloc = self.fichier.read(taille)
        self.reste -= len(bloc)
        return bloc

    def close(self):
        self.fichier.close()


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORT), RangeHandler).serve_forever()
