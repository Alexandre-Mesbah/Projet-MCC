# Q2 — Justification du sous-format de parseur

## Contexte

Le sujet du projet (UVSQ L3, version du 9 février 2026) écrit :

> On utilisera le langage de description de machine du site
> https://turingmachinesimulator.com/. **Vous pouvez restreindre ou étendre
> ce langage pour vous simplifier le travail**, par exemple interdire des
> espaces ou des sauts de ligne. Dans ce cas, il faut spécifier ces
> modifications avec un commentaire dans votre code.

Cette permission est utilisée. Le parseur principal `parser_tms.py`
n'accepte pas la syntaxe brute du site mais un **sous-format documenté**,
pensé pour être strictement déterministe, facile à parser, et facile à
relire à l'oral.

## Forme acceptée par `parser_tms.py`

Un fichier `.tm` est composé d'un en-tête à directives, puis d'une liste
de transitions :

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

Forme d'une transition :

- mono-ruban : `etat lu -> etat_suivant ecrit mouvement`
- multi-rubans : `etat lu1,lu2 -> etat_suivant ecrit1,ecrit2 mvt1,mvt2`

Mouvements acceptés : `L`, `R`, `S` avec alias `<`, `>`, `-`.

## Pourquoi ce sous-format

1. **Conformité au sujet.** L'énoncé autorise explicitement les
   restrictions. La consigne « il faut spécifier ces modifications avec un
   commentaire dans votre code » est respectée :
   - le présent fichier joue ce rôle de spécification ;
   - le module `parser_tms.py` documente la grammaire dans son docstring ;
   - le `README.md` détaille les directives et la forme des transitions.

2. **Lisibilité orale.** Une transition tient sur une ligne et se lit
   « état → état suivant, écrit, bouge ». À la soutenance on peut pointer
   une transition et expliquer son rôle sans interpréter une syntaxe à
   blocs.

3. **Déterminisme.** Pas de blocs `name:`/`init states:`/`accept
   states:`/`...` à l'indentation libre. Une ligne = une directive ou une
   transition, ce qui rend le parseur petit, total, et facile à tester.

4. **Compatibilité avec le code existant.** Toutes les machines de la
   partie 1 (Q6) sont produites par `part1_subject.py` puis sérialisées
   dans ce sous-format, et toutes les machines de démonstration sont
   écrites à la main dans le même sous-format. Le format reste donc
   homogène à l'intérieur du dépôt.

## Et le format brut du site ?

Le format brut de https://turingmachinesimulator.com/ est néanmoins
implémenté pour la **partie 2**, où il est imposé par l'énoncé : le
parseur correspondant est `parser_tm2file.py`. La machine d'exemple
`machines/part2_flip_bits.tm2` est rédigée dans la syntaxe brute du site
et utilisée par les questions 7 à 10.

Un script de conversion peut être écrit en quelques lignes pour traduire
un fichier du site vers le sous-format `.tm`, puisque les deux formats
décrivent les mêmes transitions, à la forme près.

## Résumé

- Le sous-format est une simplification autorisée par l'énoncé.
- Il est documenté ici, dans `parser_tms.py`, et dans le `README`.
- La partie 2 utilise bien le format brut du site via `parser_tm2file.py`.
