# Projet Machines de Turing

Ce dépôt contient la version centralisée du projet dans `projet.py`.

## Arborescence utile

```text
projet.py                         # point d'entree et reponses Q1 a Q11
test_badis/                       # tests separes par question et machines de test
machines/unary_multiply.tm        # machine de multiplication unaire pour Q6
```

## Lancer les questions

```bash
python3 projet.py q1
python3 projet.py q2
python3 projet.py q3
python3 projet.py q4
python3 projet.py q5
python3 projet.py q6
python3 projet.py q7
python3 projet.py q8
python3 projet.py q9
python3 projet.py q10
python3 projet.py q11
```

## Lancer les tests

Tous les tests :

```bash
python3 projet.py test
```

Un test par question :

```bash
python3 projet.py test-q1
python3 projet.py test-q2
python3 projet.py test-q3
python3 projet.py test-q4
python3 projet.py test-q5
python3 projet.py test-q6
python3 projet.py test-q7
python3 projet.py test-q8
python3 projet.py test-q9
python3 projet.py test-q10
python3 projet.py test-q11
```

## Choix de soutenance

Le coeur du projet est `projet.py`. Le dossier `test_badis/` contient les tests
et les machines utilisees par ces tests. Le dossier `machines/` ne garde que la
machine unaire necessaire a la question 6.
