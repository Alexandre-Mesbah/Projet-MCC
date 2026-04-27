# Q7 — Codage `<M>` et alphabet de travail quelconque

## Le codage retenu

Le codage strict produit par `encode_machine_strict_text` (module
`src/tm_project/encoding.py`) suit le format demandé par l'énoncé :

- séparateur unique `|` entre les champs et entre les transitions ;
- directions `L`, `S`, `R` codées par `<`, `−`, `>` ;
- état initial codé `0`, état final codé `1` ;
- les autres états sont codés par des mots de `{0,1}*` deux à deux
  distincts (`10`, `11`, `100`, `101`, ...) suivant un ordre déterministe.

L'en-tête est `blank|initial|accept|reject`, suivi des transitions sous
la forme `current|read|next|write|move`, le tout aplati avec `|`.

Exemple, machine `machines/part2_flip_bits.tm2` (qui inverse les bits) :

```text
0|0|1|10|0|0|1|0|>|0|1|0|10|>|0|10|0|1|>
```

## Que faire si on veut un alphabet de travail quelconque ?

L'énoncé pose explicitement la question. La réponse repose sur le fait
suivant : **n'importe quel alphabet fini peut être renommé sur `{0,1}*`
sans changer le comportement d'une machine de Turing, modulo un facteur
constant en taille du codage.**

### Étape 1 — Énumérer l'alphabet de travail

Soit `Σ = {a₁, a₂, ..., aₖ}` l'alphabet de travail effectif d'une
machine `M`. On le récupère mécaniquement en parcourant toutes les
transitions et en collectant les symboles lus et écrits, plus le symbole
blanc `□` déclaré dans la machine.

Dans le code, c'est fait par
`encoding._collect_strict_alphabet(machine)` : on trie l'alphabet de
manière déterministe (le blanc d'abord, puis ordre lexicographique) et on
attribue à chaque symbole un mot binaire distinct.

### Étape 2 — Choisir un codage binaire des symboles

On utilise le même schéma que pour les états : `aᵢ` reçoit le i-ème mot
binaire dans l'ordre `0, 1, 10, 11, 100, 101, ...`. Le blanc reçoit
toujours `0` par convention. Ce codage est :

- **injectif** : deux symboles distincts reçoivent deux mots binaires
  distincts ;
- **préfixe-libre dans le format flatten** : ce n'est pas le mot binaire
  qui est préfixe-libre, c'est le séparateur `|` qui rend la lecture non
  ambiguë.

### Étape 3 — Réécrire les transitions

Une transition `(q, a) → (q', b, d)` devient
`code(q) | code(a) | code(q') | code(b) | code(d)`. Le reste du codage
n'est pas touché : la structure du flatten est indépendante du nombre de
symboles, seulement de leur représentation binaire.

### Pourquoi ça suffit

Une machine `M'` qui travaille sur l'alphabet `{0, 1}` et qui simule `M`
existe automatiquement : elle lit `code(a)` au lieu de `a`, écrit
`code(b)` au lieu de `b`, et déplace ses têtes par blocs de longueur
maximale `⌈log₂ k⌉` au lieu d'un seul caractère. Le coût est :

- en **temps** : facteur `O(log k)` par étape de `M`, donc une simulation
  totale en `O(t · log k)` si `M` fait `t` étapes ;
- en **espace** : facteur `O(log k)` également.

Ce facteur est constant à machine fixée. Le pouvoir de calcul est
inchangé, ce qui justifie qu'on puisse toujours se ramener au cas binaire
sans perdre en généralité — ce qui est exactement le point exploité par
la machine universelle de la partie 2, qui prend en entrée des mots
binaires.

## Limites du codage de ce dépôt

Le codage strict actuel suppose que **chaque symbole de travail tient sur
un caractère ASCII**, conformément à la convention
`Tape` / `Configuration`. Si un alphabet manipule des « symboles » plus
longs (par exemple `foo`, `bar`, `baz`), il faudrait :

1. lever la convention « 1 symbole = 1 caractère » dans `tape.py` ;
2. adapter le parseur pour reconnaître ces symboles ;
3. la fonction de codage `encode_machine_strict_text` continue alors de
   marcher telle quelle, puisqu'elle ne fait que mapper chaque symbole sur
   un mot binaire distinct.

C'est un changement local au parseur et à la `Tape`, pas au codage.

## Résumé

- Pour un alphabet quelconque, on l'énumère, on lui attribue un codage
  binaire injectif (`0`, `1`, `10`, `11`, ...), et on réécrit chaque
  transition avec ces codes.
- Le format de flatten via `|` reste identique.
- La machine universelle de la partie 2 est donc indépendante de
  l'alphabet de travail de `M`, à un facteur logarithmique près.
