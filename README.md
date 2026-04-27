# Projet Machines de Turing Multi-rubans

## Objectif

Ce projet fournit un noyau Python 3.11+ propre, typé et testable pour :

- parser des machines de Turing dans un sous-format textuel documenté ;
- construire des configurations initiales ;
- simuler des machines mono-ruban ou multi-rubans ;
- afficher proprement les configurations, y compris en flux pour la question 5 ;
- répondre à la partie 1 en une ligne de commande question par question ;
- encoder strictement une machine mono-ruban `tm2file` en texte puis en binaire pour la partie 2 ;
- simuler les formes strictes de la machine universelle 3 rubans et de sa variante bornée 4 rubans ;
- lancer l’ensemble en ligne de commande.

Le choix général est simple : privilégier un moteur fiable, des invariants explicites, des messages d’erreur propres et une documentation honnête.

## Architecture

```text
src/tm_project/
  __init__.py
  modele.py          # Q1 : classes MT et Configuration
  ruban.py           # structure Ruban (support de modele.py)
  parseur_tm.py      # Q2 : sous-format documenté .tm
  parseur_tm2.py     # partie 2 : format brut .tm2 du site
  simulateur.py      # Q3, Q4 : un_pas() et execute()
  affichage.py       # Q5
  machines_q6.py     # Q6 : compare, recherche, mult. unaire
  codage.py          # Q7, Q8 : codages texte/binaire/entier de <M>
  universelle.py     # Q9, Q10 : MU 3 rubans + variante bornée 4 rubans
  decidabilite.py    # Q11 : preuves L1, L2, L3
  cli.py             # interface unique (cibles make q1..q11)
docs/
machines/
examples/
tests/
README.md
Makefile
pyproject.toml
requirements.txt
```

Le sommaire des modules suit l'énoncé question par question : un fichier ↔ un sujet.

## Conventions retenues

- symbole blanc unique : `_`
- un symbole de case = exactement un caractère
- machine déterministe
- un seul état final désigné par `final_state`
- les machines réponse de la partie 1 utilisent `I` comme état initial et `F` comme état final
- format de transition :
  - mono-ruban : `q0 0 -> q1 1 R`
  - multi-rubans : `q0 1,_ -> q1 0,1 R,S`
- mouvements : `L`, `R`, `S` avec alias `<`, `>`, `-`
- commentaires dans les fichiers machine :
  - lignes commençant par `;` ou `//`
  - suffixes inline ` ; ...` et ` // ...`
- `#` reste un vrai symbole de ruban
- l’entrée initiale est placée sur le ruban 1

## Format de machine accepté

Le parseur accepte un sous-ensemble textuel documenté, inspiré de Turing Machine Simulator :

```text
name: demo_flip_bits
init: q0
final: qf
blank: _
tapes: 1
q0 0 -> q0 1 R
q0 1 -> q0 0 R
q0 _ -> qf _ S
```

Directives reconnues :

- `name:`
- `init:`
- `final:`
- `blank:` optionnelle, défaut `_`
- `tapes:` optionnelle, défaut `1`
- `states:` optionnelle

Le parseur vérifie :

- la présence des directives obligatoires ;
- la cohérence du nombre de rubans ;
- la forme des transitions ;
- l’absence de doublons déterministes ;
- l’usage éventuel d’états non déclarés dans `states:`.

## Simulation

Le module `simulator.py` expose :

- `step(machine, config)`
- `run(machine, input_word, max_steps=None)`
- `run_stream(machine, input_word, max_steps=None)`
- `run_verbose(machine, input_word, max_steps=None)`

Statuts d’exécution :

- `running` : exécution en cours
- `accepted` : état final atteint
- `rejected` : état de rejet explicite atteint, ou transition absente dans une machine `tm2file`
- `blocked` : aucune transition applicable
- `timeout` : borne `max_steps` atteinte sans arrêt réel

Choix importants :

- `step()` ne mute jamais silencieusement la configuration d’entrée ;
- un blocage n’est pas confondu avec une acceptation ;
- un timeout signifie uniquement que la borne a été atteinte, pas que la machine a terminé.

## Affichage

Le module `display.py` fournit :

- `format_configuration(config, radius=10)`
- `format_configuration_detailed(config, radius=10)`

Exemple compact :

```text
Step 3 | State: qf | Status: accepted
Reason: Reached the final state.
Tape 1: _ _ 1 0 _ _
              ^
```

## Encodage textuel et binaire

Le module `encoding.py` conserve l’ancien encodage interne pour les commandes historiques, et ajoute un encodage strict pour la partie 2.

### Partie 2 stricte : format d’entrée `tm2file`

Le parseur strict est dans `parser_tm2file.py`. Il lit le format `tm2file` de Turing Machine Simulator :

```text
_ q0 qA qR
q0 0 q0 1 R
q0 1 q0 0 R
q0 _ qA _ R
```

Règles retenues :

- première ligne : `blank initial accept reject` ;
- transitions : `current read next write direction` ;
- `read` accepte des alternatives séparées par `,`, par exemple `0,1` ;
- `write = .` conserve le symbole lu ;
- seuls `L` et `R` sont acceptés par le parseur `tm2file`, comme dans le site ;
- le texte après le 5e champ d’une transition est ignoré ;
- une ligne vide après l’en-tête termine la liste des transitions ;
- une transition absente mène à l’état de rejet explicite.

### Codage strict Q7/Q8

Pour la partie 2, `encode_machine_strict_text()` produit une chaîne sans préfixe `blank=` et sans séparateur `||`. Tous les champs sont séparés par `|`.

Format :

```text
blank|initial|accept|reject|current|read|next|write|move|...
```

Conventions :

- état initial : `0` ;
- état acceptant : `1` ;
- état rejetant : `10` ;
- autres états : `11`, `100`, `101`, ... par ordre déterministe ;
- symbole blanc : `0` ;
- autres symboles de travail : mots binaires déterministes, ce qui permet d’accepter n’importe quel alphabet de travail représenté par des symboles d’un caractère ;
- directions : `L -> <`, `S -> -`, `R -> >`.

Exemple pour `machines/part2_flip_bits.tm2` :

```text
0|0|1|10|0|0|1|0|>|0|1|0|10|>|0|10|0|1|>
```

L’encodage binaire Q8 est l’ASCII 8 bits de cette chaîne stricte. La fonction dédiée `encode_tm2file_text_to_binary(source)` parse une chaîne `tm2file` et renvoie directement ce binaire.

### Ancien encodage interne

Conventions :

- l’état initial est renommé en `0`
- l’état final est renommé en `1`
- les autres états sont renommés en `2`, `3`, ... par ordre lexicographique
- chaque transition devient `etat|lu|ecrit|direction|etat_suivant`
- les transitions sont séparées par `||`
- la chaîne commence par `blank=<symbole>`

Exemple :

```text
blank=_||0|0|1|>|0||0|1|0|>|0||0|_|_|-|1
```

L’encodage binaire est simplement l’ASCII 8 bits de cette chaîne. Ce choix est injectif, facile à expliquer et facile à décoder.

## Machine universelle stricte

Le module `strict_universal.py` fournit les entrées strictes de la partie 2.

Q9 utilise `strict_universal_simulate_word(word)` avec un seul mot :

```text
<M>#x
```

`<M>` est le codage strict de la machine, et `x` est la suite des symboles déjà renommés en mots binaires, séparés par `|`. Le résultat expose trois rubans :

- ruban 1 : description encodée de `M` ;
- ruban 2 : ruban simulé final de `M` sur `x` ;
- ruban 3 : travail, avec état courant, compteur de pas, statut et dernière transition inspectée.

Q10 utilise `strict_bounded_universal_simulate_word(word)` avec un seul mot :

```text
<M>#x#n
```

`n` est un entier binaire non signé. Le résultat ajoute un 4e ruban compteur en unaire `1^n`, décrémenté à chaque pas simulé. Quand le compteur atteint 0 avant l’arrêt, le statut est `timeout`.

Le fichier `universal.py` reste présent pour l’ancienne commande générale du projet, mais la conformité stricte de la partie 2 passe par `strict_universal.py`.

## Décidabilité Q11

Le module `deciders_notes.py` donne les preuves pour L1, L2 et L3. Pour L3, la convention retenue est explicitement : “M calcule la même chose sur x et y” signifie que les deux calculs terminent et produisent le même mot de sortie.

Une version rédigée et plus complète des preuves est disponible dans [`docs/Q11_decidabilite.md`](docs/Q11_decidabilite.md).

## Documentation complémentaire

Le dossier `docs/` contient des notes rédigées qui complètent le code :

- [`docs/Q2_parser.md`](docs/Q2_parser.md) — justification du sous-format de parseur (la consigne autorise les restrictions documentées) ;
- [`docs/Q6_bonus.md`](docs/Q6_bonus.md) — note explicite : la multiplication binaire bonus n'est pas implémentée ;
- [`docs/Q7_alphabet.md`](docs/Q7_alphabet.md) — discussion détaillée du codage `<M>` et du traitement d'un alphabet de travail quelconque ;
- [`docs/Q11_decidabilite.md`](docs/Q11_decidabilite.md) — preuves complètes de décidabilité de L1, L2 et L3.

## CLI

La CLI principale conserve les commandes générales et la partie 2 :

```bash
python -m tm_project.cli run --machine machines/demo_flip_bits.tm --input 0101
python -m tm_project.cli run --machine machines/demo_flip_bits.tm --input 0101 --verbose
python -m tm_project.cli encode --machine machines/demo_flip_bits.tm
python -m tm_project.cli universal --machine machines/demo_flip_bits.tm --input 0101
python -m tm_project.cli bounded-universal --machine machines/demo_flip_bits.tm --input 0101 --steps 5
python -m tm_project.cli part2-report --machine machines/part2_flip_bits.tm2 --input 0101
python -m tm_project.cli strict-universal --machine machines/part2_flip_bits.tm2 --input 0101
python -m tm_project.cli strict-bounded-universal --machine machines/part2_flip_bits.tm2 --input 0101 --steps 5
python -m tm_project.cli q11
```

La CLI intercepte les erreurs utilisateur courantes pour éviter une stack trace brute sur un mauvais fichier, un mauvais argument ou un usage incohérent.

Le repo fournit aussi des commandes dédiées par question :

```bash
make q1
make q2
make q3
make q4
make q5
make q6
make q7
make q8
make q9
make q10
make q11
```

Les cibles de tests dédiées sont également fournies :

```bash
make test-q1
make test-q2
make test-q3
make test-q4
make test-q5
make test-q6
make test-part2
```

## Catalogue des machines fournies

### Machines entièrement validées par les tests

- `machines/strict_flip_bits.tm`
  - machine d’exemple stricte pour les questions 2 à 5, avec `I` et `F`
- `machines/demo_flip_bits.tm`
  - retourne le complément bit à bit d’un mot binaire et s’arrête sur blanc
- `machines/part2_flip_bits.tm2`
  - machine strictement au format `tm2file` pour les questions 7 à 10
- `machines/demo_copy_2tapes.tm`
  - copie le contenu du ruban 1 sur le ruban 2
- `machines/demo_loop.tm`
  - boucle volontairement, utile pour tester `timeout`
- `machines/compare_binary.tm`
  - machine générale de comparaison binaire pour la question 6
  - s’arrête si et seulement si `x < y`, boucle sinon
- `machines/search_list.tm`
  - machine générale de recherche dans une liste pour la question 6
  - s’arrête si et seulement si `x = wi` pour un des `wi`
- `machines/unary_multiply.tm`
  - machine générale de multiplication unaire pour la question 6
  - laisse `1^(n*m)` sur le ruban 1

Ces machines sont générées et sérialisées par `src/tm_project/part1_subject.py`, puis testées sur des cas multi-symboles.

## Tests

Les tests couvrent :

- invariants du modèle ;
- invariants du ruban ;
- parsing ;
- simulation mono-ruban et multi-rubans ;
- affichage progressif ;
- affichage ;
- questions 1 à 6 séparément ;
- encodage ;
- parsing, encodage et simulation stricte partie 2 ;
- simulation universelle ;
- smoke tests CLI.

Commandes utiles :

```bash
make check
make test-part1
make test-part2
make run-example
make encode-example
make universal-example
```

Ou directement :

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m pytest -q tests/test_question6.py
```

## Contrat strict partie 2

La partie 2 n’utilise plus le sous-format `.tm` du parseur historique : elle passe par `parser_tm2file.py`, par le codage strict sans `blank=` ni `||`, et par les entrées uniques `<M>#x` et `<M>#x#n` pour Q9 et Q10.
