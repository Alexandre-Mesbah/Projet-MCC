# Q6 — Bonus multiplication binaire (non traité)

## Statut

**La question bonus de la Q6 — multiplication binaire — n'est pas
implémentée dans ce rendu.** Elle est volontairement omise.

L'énoncé la formule ainsi :

> (Bonus) Multiplication en binaire : à partir d'une entrée x#y, produire
> la sortie x \* y où x et y sont des entiers en binaire. Vous utiliserez
> le même algo lent que pour la multiplication en unaire en ajoutant y
> fois x.

Comme indiqué par le mot « Bonus », cette question n'est pas obligatoire.
Les trois questions obligatoires de la Q6 sont, elles, bien traitées et
testées :

- comparaison d'entiers binaires : `machines/compare_binary.tm` ;
- recherche dans une liste : `machines/search_list.tm` ;
- multiplication unaire : `machines/unary_multiply.tm`.

## Squelette d'algorithme retenu si on l'avait traitée

L'énoncé fixe l'algorithme : « ajouter y fois x ». Une machine
multi-rubans simple suit la structure :

1. Ruban 1 : entrée `x#y`, à la fin écraser par le produit en binaire.
2. Ruban 2 : copie de `x` (le terme à ajouter).
3. Ruban 3 : copie de `y` (le compteur, à décrémenter en binaire).
4. Ruban 4 : accumulateur, initialisé à `0`, où on cumule les additions
   binaires de `x`.

Boucle :

- tant que le ruban 3 n'est pas nul, on additionne le contenu du ruban 2
  au ruban 4 (addition binaire avec retenue, traitée bit à bit en partant
  des poids faibles), puis on décrémente le ruban 3 d'une unité en
  binaire.
- quand le ruban 3 vaut zéro, on recopie le ruban 4 sur le ruban 1 et on
  passe à l'état final.

L'addition binaire avec retenue et le décrément binaire sont des
sous-machines classiques ; leur écriture explicite avec le `PatternMachineBuilder`
de `part1_subject.py` représente un volume de transitions important
(plusieurs dizaines), ce qui justifie de la traiter à part comme un vrai
exercice de bonus.

## Pourquoi le signaler explicitement

La consigne du projet insiste sur la maîtrise du rendu en soutenance :

> Une méconnaissance manifeste du travail rendu, et une réponse du type
> « je ne me souviens plus, je l'ai fait il y a longtemps » entrainera
> un zéro pour le projet.

On préfère donc dire clairement : **le bonus binaire n'a pas été traité**,
plutôt que de masquer l'absence sous une implémentation incomplète. Les
trois fonctions obligatoires sont toutes présentes, vérifiées par
`tests/test_question6.py`, et exécutables via `make q6`.
