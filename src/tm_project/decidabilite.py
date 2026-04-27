"""Concise decidability notes for the oral presentation."""

DECIDABILITY_NOTES = """
L1 = {<M>#n | M s'arrête sur n en moins de n étapes}
Décidable.
Idée : on simule M sur n pendant au plus n - 1 étapes. Le nombre d'étapes à tester est borné
par l'entrée, donc l'algorithme termine toujours.

L2 = {<M>#n | M s'arrête sur tous les mots de taille n}
Indécidable, mais semi-décidable.
Idée d'indécidabilité : pour un problème d'arrêt donné <M>, on construit une machine M'
qui ignore son entrée et simule M sur le mot fixé voulu. Alors M' s'arrête sur tous les mots
de taille n si et seulement si M s'arrête sur cette entrée. On réduit donc le problème d'arrêt
à L2.
Pourquoi semi-décidable : pour une longueur n fixée, il n'y a qu'un nombre fini de mots de
taille n. On peut lancer les simulations en parallèle et accepter dès qu'elles ont toutes
terminé.

L3 = {<M>#x#y | M calcule la même chose sur x et y}
Convention retenue : "même chose" signifie ici que M s'arrête sur x et sur y, et produit le
même mot de sortie sur son ruban final dans les deux cas.
Avec cette convention, L3 est semi-décidable mais indécidable.
Pourquoi semi-décidable : on exécute M sur x et sur y en parallèle ; si les deux calculs
terminent et donnent la même sortie, on accepte.
Pourquoi indécidable : à partir d'une instance <M, w> du problème d'arrêt, on construit N tel
que N(y) s'arrête immédiatement avec la sortie 0, et N(x) simule M sur w puis écrit 0 si la
simulation termine. Alors N calcule la même chose sur x et y si et seulement si M s'arrête sur w.
Le problème d'arrêt se réduit donc à L3.
""".strip()


def get_decidability_notes() -> str:
    """Return the bundled decidability notes."""
    return DECIDABILITY_NOTES
