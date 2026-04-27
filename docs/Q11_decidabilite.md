# Q11 — Décidabilité de L1, L2, L3

On note `<M>` un codage de la machine de Turing `M` (par exemple celui
de la partie 2 de ce projet). Par convention, `n` est un entier en
binaire et `x`, `y` sont des mots de `{0, 1}*`.

## L1 = { ⟨M⟩#n | M s'arrête sur n en moins de n étapes }

**L1 est décidable.**

### Algorithme de décision

Sur entrée `<M>#n` :

1. Décoder `n` (binaire → entier) ; soit `N` cette valeur.
2. Initialiser une simulation de `M` sur l'entrée `n` (en tant que mot).
3. Exécuter au plus `N − 1` pas de simulation. À chaque pas :
   - si `M` atteint son état final, **accepter** ;
   - sinon continuer.
4. Si la borne `N − 1` est atteinte sans arrêt, **rejeter**.

### Justification

La borne `N − 1` est finie et calculable depuis l'entrée. La machine
universelle bornée Q10 (`strict_bounded_universal_simulate_word`) est
exactement un décideur de ce type : elle simule `M` sur `x` pendant `n`
étapes au plus et émet `accepted`, `rejected` ou `timeout` en temps fini.

Le décideur décrit ci-dessus est donc une instance de cette machine, où
on identifie `timeout` à un rejet pour L1. L'algorithme termine toujours,
L1 est donc décidable.

## L2 = { ⟨M⟩#n | M s'arrête sur tous les mots de taille n }

**L2 est indécidable, mais semi-décidable.**

### Indécidabilité — réduction depuis le problème d'arrêt

On réduit `HALT = { ⟨M, w⟩ | M s'arrête sur w }` à L2.

Étant donné `⟨M, w⟩`, on construit une machine `M'` qui :

- ignore son propre mot d'entrée ;
- simule `M` sur le mot fixé `w` ;
- s'arrête si et seulement si la simulation s'arrête.

Alors :

- si `M` s'arrête sur `w`, `M'` s'arrête sur n'importe quel mot, donc en
  particulier sur tous les mots de taille `n` pour tout `n`. Donc
  `⟨M'⟩#n ∈ L2` pour tout `n` choisi à l'avance ;
- si `M` ne s'arrête pas sur `w`, `M'` ne s'arrête sur aucun mot, donc
  `⟨M'⟩#n ∉ L2` pour tout `n`.

On choisit par exemple `n = 0` (le mot vide est le seul mot de taille
0). On a alors

`⟨M'⟩#0 ∈ L2 ⟺ M s'arrête sur w`,

ce qui ramène le problème d'arrêt à L2. L2 n'est donc pas décidable.

### Semi-décidabilité

Pour une longueur `n` fixée il n'y a que `2ⁿ` mots à tester, ce qui est
fini. On lance les `2ⁿ` simulations en parallèle, par exemple en
alternant un pas pour chacune (dovetailing). Dès que les `2ⁿ` simulations
ont toutes terminé, on **accepte**.

- Si `M` s'arrête sur tous les mots de taille `n`, chaque simulation
  termine en temps fini, donc l'algorithme accepte en temps fini ;
- sinon, au moins une simulation ne s'arrête jamais et l'algorithme
  boucle.

L2 est donc dans `RE`, c'est-à-dire semi-décidable.

L2 n'est en revanche pas dans `coRE` : un algorithme qui rejetterait
pourrait conclure qu'au moins un mot de taille `n` ne s'arrête jamais,
ce qui sémi-déciderait le complément du problème d'arrêt — impossible.

## L3 = { ⟨M⟩#x#y | M calcule la même chose sur x et y }

### Convention retenue

La phrase « M calcule la même chose sur x et y » est ambiguë. On retient
la convention :

> M s'arrête sur x **et** s'arrête sur y, **et** produit le même mot de
> sortie sur son ruban final dans les deux cas.

C'est la convention la plus utile car elle évite de raisonner sur des
exécutions infinies, et elle est suffisante pour les preuves qui suivent.

### L3 est semi-décidable

Algorithme de semi-décision sur `⟨M⟩#x#y` :

1. simuler `M(x)` et `M(y)` en parallèle (un pas chacun à tour de rôle) ;
2. si les deux simulations s'arrêtent, comparer les sorties ;
3. accepter si et seulement si elles sont égales.

Si `⟨M⟩#x#y ∈ L3`, les deux simulations s'arrêtent et l'algorithme
accepte en temps fini. Si `⟨M⟩#x#y ∉ L3`, soit l'une des simulations ne
termine pas et l'algorithme boucle, soit elles produisent des sorties
différentes et l'algorithme rejette.

L3 est donc semi-décidable.

### L3 est indécidable — réduction depuis le problème d'arrêt

À partir d'une instance `⟨M, w⟩` du problème d'arrêt, on construit une
machine `N` qui :

- sur l'entrée `y` : s'arrête immédiatement avec la sortie `0` ;
- sur l'entrée `x` : simule `M` sur `w`, puis si la simulation s'arrête,
  écrit `0` sur son ruban de sortie et s'arrête.

Alors :

- si `M` s'arrête sur `w`, `N(x) = 0 = N(y)`, donc
  `⟨N⟩#x#y ∈ L3` ;
- si `M` ne s'arrête pas sur `w`, `N(x)` ne s'arrête pas, donc la
  convention « `M` s'arrête sur les deux » échoue et
  `⟨N⟩#x#y ∉ L3`.

`HALT` se réduit donc à L3, qui n'est pas décidable.

### Bilan pour L3

L3 ∈ `RE \ R`, c'est-à-dire semi-décidable mais pas décidable.

## Résumé

| Langage | Statut                       |
| ------- | ---------------------------- |
| L1      | décidable                    |
| L2      | semi-décidable, indécidable  |
| L3      | semi-décidable, indécidable  |

Une version condensée de ces preuves est disponible à l'exécution via
`make q11`, qui appelle `get_decidability_notes()` du module
`src/tm_project/deciders_notes.py`.
