from pathlib import Path
import runpy
import sys


# // Conventions du projet :
# // - le symbole blanc est represente par "_".
# // - les mouvements acceptes sont R ou >, L ou <, S ou -.
# // - les machines de la partie 1 peuvent avoir plusieurs rubans.
# // - les machines de la partie 2 sont limitees a un seul ruban, comme demande dans l'enonce.
# // - les formats acceptes sont documentes juste au-dessus des fonctions de lecture.


class Machine_turing:
    def __init__(self, alphabet, transitions, etat_initial, etat_acceptant, blanc, nb_rubans):
        self.alphabet = alphabet
        self.transitions = transitions
        self.etat_initial = etat_initial
        self.etat_acceptant = etat_acceptant
        self.blanc = blanc
        self.nb_rubans = nb_rubans


class Configuration:
    def __init__(self, rubans, positions, etat):
        self.rubans = rubans
        self.positions = positions
        self.etat = etat


def un_pas(machine, config):
    symboles_lus = []

    for i in range(machine.nb_rubans):
        position = config.positions[i]
        ruban = config.rubans[i]

        if position < 0:
            ruban.insert(0, machine.blanc)
            config.positions[i] = 0
            position = 0

        if position >= len(ruban):
            ruban.append(machine.blanc)

        symboles_lus.append(ruban[position])

    if machine.nb_rubans == 1:
        cle = (config.etat, symboles_lus[0])
    else:
        cle = (config.etat, tuple(symboles_lus))

    if cle not in machine.transitions:
        return None

    nouvel_etat, symboles_ecrits, directions = machine.transitions[cle]

    if machine.nb_rubans == 1:
        symboles_ecrits = [symboles_ecrits]
        directions = [directions]

    for i in range(machine.nb_rubans):
        position = config.positions[i]
        config.rubans[i][position] = symboles_ecrits[i]

    config.etat = nouvel_etat

    for i in range(machine.nb_rubans):
        direction = directions[i]

        if direction in ("R", ">"):
            config.positions[i] += 1
        elif direction in ("L", "<"):
            config.positions[i] -= 1
            if config.positions[i] < 0:
                config.rubans[i].insert(0, machine.blanc)
                config.positions[i] = 0
        elif direction in ("S", "-"):
            pass
        else:
            raise ValueError("Direction inconnue : " + direction)

        if config.positions[i] >= len(config.rubans[i]):
            config.rubans[i].append(machine.blanc)

    return config


# // Sous-formats acceptes pour la partie 1 :
# // - format Badis en deux lignes par transition :
# //   etat_source,symbole_lu_ruban1,...,symbole_lu_ruban_k
# //   etat_destination,symbole_ecrit_ruban1,...,symbole_ecrit_ruban_k,direction1,...,directionk
# // - format inspire du site Turing Machine Simulator :
# //   etat_source symboles_lus -> etat_destination symboles_ecrits directions
# // - directives reconnues : name:, init:, accept:, final:, blank:, tapes:.
# // - les virgules servent de separateurs dans le format Badis.
# // - les lignes vides, les lignes commencant par ";" et les lignes commencant par "//" sont ignorees.
def lire_machine(chemin_fichier):
    with open(chemin_fichier, "r", encoding="utf-8") as f:
        lignes = []
        for ligne in f:
            ligne = ligne.strip()
            if ligne and not ligne.startswith(";") and not ligne.startswith("//"):
                lignes.append(ligne)

    etat_initial = None
    etat_acceptant = None
    transitions = {}
    alphabet = set()
    blanc = "_"
    nb_rubans = 1

    i = 0
    while i < len(lignes):
        ligne = lignes[i]

        if ligne.startswith("name:"):
            i += 1
        elif ligne.startswith("init:"):
            etat_initial = ligne.split(":", 1)[1].strip()
            i += 1
        elif ligne.startswith("accept:") or ligne.startswith("final:"):
            etat_acceptant = ligne.split(":", 1)[1].strip()
            i += 1
        elif ligne.startswith("blank:"):
            blanc = ligne.split(":", 1)[1].strip()
            i += 1
        elif ligne.startswith("tapes:"):
            nb_rubans = int(ligne.split(":", 1)[1].strip())
            i += 1
        elif " -> " in ligne:
            etat_source, symboles_lus, etat_destination, symboles_ecrits, directions = _parser_transition_fleche(ligne)
            nb_rubans = len(symboles_lus)
            _ajouter_transition(transitions, alphabet, nb_rubans, etat_source, symboles_lus, etat_destination, symboles_ecrits, directions)
            i += 1
        else:
            if i + 1 >= len(lignes):
                raise ValueError("Transition incomplete dans le fichier machine.")
            etat_source, symboles_lus, etat_destination, symboles_ecrits, directions = _parser_transition_deux_lignes(lignes[i], lignes[i + 1])
            nb_rubans = len(symboles_lus)
            _ajouter_transition(transitions, alphabet, nb_rubans, etat_source, symboles_lus, etat_destination, symboles_ecrits, directions)
            i += 2

    return Machine_turing(alphabet, transitions, etat_initial, etat_acceptant, blanc, nb_rubans)


def _parser_transition_deux_lignes(condition, instruction):
    morceaux_condition = [m.strip() for m in condition.split(",")]
    morceaux_instruction = [m.strip() for m in instruction.split(",")]

    etat_source = morceaux_condition[0]
    symboles_lus = morceaux_condition[1:]
    etat_destination = morceaux_instruction[0]
    reste_instruction = morceaux_instruction[1:]

    nb_rubans = len(symboles_lus)
    if len(reste_instruction) != 2 * nb_rubans:
        raise ValueError("Transition invalide : symboles ecrits et directions incoherents.")

    symboles_ecrits = reste_instruction[:nb_rubans]
    directions = reste_instruction[nb_rubans:]
    return etat_source, symboles_lus, etat_destination, symboles_ecrits, directions


def _parser_transition_fleche(ligne):
    gauche, droite = ligne.split(" -> ", 1)
    etat_source, symboles_lus = gauche.split(maxsplit=1)
    morceaux_droite = droite.split(maxsplit=2)

    if len(morceaux_droite) != 3:
        raise ValueError("Transition invalide au format fleche.")

    etat_destination = morceaux_droite[0]
    symboles_ecrits = morceaux_droite[1]
    directions = morceaux_droite[2]

    return (
        etat_source,
        [s.strip() for s in symboles_lus.split(",")],
        etat_destination,
        [s.strip() for s in symboles_ecrits.split(",")],
        [s.strip() for s in directions.split(",")],
    )


def _ajouter_transition(transitions, alphabet, nb_rubans, etat_source, symboles_lus, etat_destination, symboles_ecrits, directions):
    if len(symboles_lus) != nb_rubans or len(symboles_ecrits) != nb_rubans or len(directions) != nb_rubans:
        raise ValueError("Transition invalide : nombre de rubans incoherent.")

    if nb_rubans == 1:
        cle = (etat_source, symboles_lus[0])
        valeur = (etat_destination, symboles_ecrits[0], directions[0])
    else:
        cle = (etat_source, tuple(symboles_lus))
        valeur = (etat_destination, tuple(symboles_ecrits), tuple(directions))

    for symbole in symboles_lus + symboles_ecrits:
        alphabet.add(symbole)

    transitions[cle] = valeur


def configuration_initiale(mot, machine):
    premier_ruban = list(mot)

    if premier_ruban == []:
        premier_ruban = [machine.blanc]
    else:
        premier_ruban.append(machine.blanc)

    rubans = [premier_ruban]
    for _ in range(machine.nb_rubans - 1):
        rubans.append([machine.blanc])

    positions = [0] * machine.nb_rubans
    return Configuration(rubans, positions, machine.etat_initial)


def simuler_mot(mot, machine, max_etapes=None):
    config = configuration_initiale(mot, machine)
    nb_etapes = 0

    while config.etat != machine.etat_acceptant:
        if max_etapes is not None and nb_etapes >= max_etapes:
            return config, False

        nouvelle_config = un_pas(machine, config)
        if nouvelle_config is None:
            return config, False

        config = nouvelle_config
        nb_etapes += 1

    return config, True


def afficher_configuration(config):
    print("Etat :", config.etat)

    for i in range(len(config.rubans)):
        ruban = "".join(config.rubans[i])
        tete = " " * config.positions[i] + "^"
        print(f"Ruban {i + 1} : {ruban}")
        print(f"          {tete}")


def simuler_mot_affichage(mot, machine, max_etapes=1000):
    config = configuration_initiale(mot, machine)
    nb_etapes = 0

    print("Configuration initiale :")
    afficher_configuration(config)

    while config.etat != machine.etat_acceptant and nb_etapes < max_etapes:
        nouvelle_config = un_pas(machine, config)

        if nouvelle_config is None:
            print("La machine est bloquee.")
            return config, False

        config = nouvelle_config
        nb_etapes += 1

        print(f"Apres l'etape {nb_etapes} :")
        afficher_configuration(config)

    return config, config.etat == machine.etat_acceptant


# // Sous-format accepte pour la partie 2 :
# // - seules les machines a un seul ruban sont acceptees.
# // - chaque transition est ecrite sur deux lignes consecutives ou au format fleche.
# // - les etats sont recodes en mots binaires : etat initial -> 0, etat final -> 1.
# // - les autres etats sont codes par 10, 11, 100, ... selon leur ordre de lecture.
def lire_machine2(chemin_fichier):
    machine = lire_machine(chemin_fichier)

    if machine.nb_rubans != 1:
        raise ValueError("La partie 2 accepte seulement les machines a un ruban.")

    codes_etats = {machine.etat_initial: "0", machine.etat_acceptant: "1"}
    prochain_code = 2

    for (etat_source, _), (etat_destination, _, _) in machine.transitions.items():
        if etat_source not in codes_etats:
            codes_etats[etat_source] = bin(prochain_code)[2:]
            prochain_code += 1
        if etat_destination not in codes_etats:
            codes_etats[etat_destination] = bin(prochain_code)[2:]
            prochain_code += 1

    morceaux = []
    for (etat_source, symbole_lu), (etat_destination, symbole_ecrit, direction) in machine.transitions.items():
        morceaux.extend([
            codes_etats[etat_source],
            symbole_lu,
            symbole_ecrit,
            direction,
            codes_etats[etat_destination],
        ])

    return "|".join(morceaux)


# // Codage binaire choisi pour Q8 :
# // - 0 -> 000
# // - 1 -> 001
# // - | -> 010
# // - _ -> 011
# // - < ou L -> 100
# // - - ou S -> 101
# // - > ou R -> 110
# // Pour accepter n'importe quel alphabet de travail, il faudrait d'abord coder
# // chaque symbole ASCII avec un codage injectif de longueur fixe ou prefixe.
def coder_binaire(chaine):
    codage_binaire = {
        "0": "000",
        "1": "001",
        "|": "010",
        "_": "011",
        "<": "100",
        "-": "101",
        ">": "110",
        "L": "100",
        "S": "101",
        "R": "110",
    }

    resultat = ""
    for caractere in chaine:
        if caractere not in codage_binaire:
            raise ValueError("Caractere non code en binaire : " + caractere)
        resultat += codage_binaire[caractere]

    return resultat


def coder_machine_texte_binaire(chaine_machine):
    chemin_temporaire = Path("test_badis/_machine_temporaire.txt")
    chemin_temporaire.write_text(chaine_machine, encoding="utf-8")
    try:
        return coder_binaire(lire_machine2(chemin_temporaire))
    finally:
        chemin_temporaire.unlink(missing_ok=True)


def lire_machine_binaire(chemin_fichier):
    code_machine = lire_machine2(chemin_fichier)
    return coder_binaire(code_machine)


def convertie_binaire(chaine_binaire):
    return int(chaine_binaire, 2)


def decoder_machine_code(code_machine):
    morceaux = code_machine.split("|")

    if len(morceaux) % 5 != 0:
        raise ValueError("Le code de la machine est invalide.")

    transitions = {}
    alphabet = set()

    for i in range(0, len(morceaux), 5):
        etat_source = morceaux[i]
        symbole_lu = morceaux[i + 1]
        symbole_ecrit = morceaux[i + 2]
        direction = morceaux[i + 3]
        etat_destination = morceaux[i + 4]

        transitions[(etat_source, symbole_lu)] = (etat_destination, symbole_ecrit, direction)
        alphabet.add(symbole_lu)
        alphabet.add(symbole_ecrit)

    return Machine_turing(alphabet, transitions, "0", "1", "_", 1)


def ruban_avec_tete(ruban, position):
    ruban_marque = []

    for i in range(len(ruban)):
        symbole = ruban[i]
        if i == position:
            ruban_marque.append(symbole + "*")
        else:
            ruban_marque.append(symbole)

    return " ".join(ruban_marque)


def afficher_rubans_universelle(ruban1, ruban2, ruban3, etape, ruban4=None):
    print(f"Etape {etape} :")
    print("Ruban 1 :", ruban1)
    print("Ruban 2 :", ruban2)
    print("Ruban 3 :", ruban3)
    if ruban4 is not None:
        print("Ruban 4 :", ruban4)
    print()


def machine_universelle(entree, affichage=False, max_etapes=None):
    code_machine, mot = entree.split("#", 1)
    machine = decoder_machine_code(code_machine)
    config = configuration_initiale(mot, machine)

    ruban1 = entree
    ruban2 = code_machine + "#" + config.etat
    ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])
    nb_etapes = 0

    if affichage:
        afficher_rubans_universelle(ruban1, ruban2, ruban3, nb_etapes)

    while config.etat != machine.etat_acceptant:
        if max_etapes is not None and nb_etapes >= max_etapes:
            return ruban1, ruban2, ruban3, False

        nouvelle_config = un_pas(machine, config)
        if nouvelle_config is None:
            ruban2 = code_machine + "#blocage"
            ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])
            return ruban1, ruban2, ruban3, False

        config = nouvelle_config
        nb_etapes += 1

        ruban2 = code_machine + "#" + config.etat
        ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])

        if affichage:
            afficher_rubans_universelle(ruban1, ruban2, ruban3, nb_etapes)

    return ruban1, ruban2, ruban3, True


def machine_universelle_n_etapes(entree, affichage=False):
    parties = entree.split("#")

    if len(parties) != 3:
        raise ValueError("Entree attendue : <M>#x#n")

    code_machine, mot, etape = parties
    machine = decoder_machine_code(code_machine)
    config = configuration_initiale(mot, machine)
    compteur_restant = int(etape)

    ruban1 = entree
    ruban2 = code_machine + "#" + config.etat
    ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])
    ruban4 = "1" * compteur_restant + "_"
    nb_etapes = 0

    if affichage:
        afficher_rubans_universelle(ruban1, ruban2, ruban3, nb_etapes, ruban4)

    while config.etat != machine.etat_acceptant and compteur_restant > 0:
        nouvelle_config = un_pas(machine, config)

        if nouvelle_config is None:
            ruban2 = code_machine + "#blocage"
            ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])
            ruban4 = "1" * compteur_restant + "_"
            return ruban1, ruban2, ruban3, ruban4, False

        config = nouvelle_config
        nb_etapes += 1
        compteur_restant -= 1

        ruban2 = code_machine + "#" + config.etat
        ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])
        ruban4 = "1" * compteur_restant + "_"

        if affichage:
            afficher_rubans_universelle(ruban1, ruban2, ruban3, nb_etapes, ruban4)

    return ruban1, ruban2, ruban3, ruban4, config.etat == machine.etat_acceptant


def preuves_q11():
    return (
        "L1 est decidable : on simule M sur n pendant au plus n etapes.\n"
        "L2 est indecidable : savoir si M s'arrete sur tous les mots de taille n generalise le probleme de l'arret.\n"
        "L3 est indecidable : savoir si M calcule la meme chose sur x et y generalise l'equivalence de comportements de machines."
    )


def _chemin_test(nom):
    return Path(__file__).resolve().parent / "test_badis" / nom


def demo_q1():
    machine = Machine_turing({"0", "1"}, {("I", "0"): ("F", "1", "S")}, "I", "F", "_", 1)
    config = Configuration([["0", "_"]], [0], "I")
    print("Machine :", machine.__dict__)
    print("Configuration :", config.__dict__)


def demo_q2():
    machine = lire_machine(_chemin_test("test.txt"))
    config = configuration_initiale("0011", machine)
    afficher_configuration(config)


def demo_q3():
    machine = lire_machine(_chemin_test("test.txt"))
    config = configuration_initiale("0011", machine)
    un_pas(machine, config)
    afficher_configuration(config)


def demo_q4():
    machine = lire_machine(_chemin_test("test.txt"))
    config, accepte = simuler_mot("0011", machine)
    afficher_configuration(config)
    print("Accepte :", accepte)


def demo_q5():
    machine = lire_machine(_chemin_test("test.txt"))
    simuler_mot_affichage("0011", machine)


def demo_q6():
    machine_compare = lire_machine(_chemin_test("comparaison_x_inf_y.txt"))
    _, accepte_compare = simuler_mot("10#11", machine_compare, max_etapes=1000)
    print("Comparaison 10#11 :", accepte_compare)

    machine_recherche = lire_machine(_chemin_test("recherche_dans_liste.txt"))
    _, accepte_recherche = simuler_mot("10#0#10#11", machine_recherche, max_etapes=1000)
    print("Recherche 10#0#10#11 :", accepte_recherche)

    machine_mult = lire_machine(Path(__file__).resolve().parent / "machines" / "unary_multiply.tm")
    config, accepte_mult = simuler_mot("11#111", machine_mult, max_etapes=5000)
    print("Multiplication unaire 11#111 :", "".join(config.rubans[0]).strip("_"), accepte_mult)


def demo_q7():
    code = lire_machine2(_chemin_test("test.txt"))
    print(code)
    print("Pour accepter n'importe quel alphabet, il faut coder chaque symbole ASCII avec un code injectif.")


def demo_q8():
    code = lire_machine2(_chemin_test("test.txt"))
    code_binaire = coder_binaire(code)
    print("Codage :", code)
    print("Binaire :", code_binaire)
    print("Entier :", convertie_binaire(code_binaire))


def demo_q9():
    ruban1, ruban2, ruban3, accepte = machine_universelle("0|0|1|>|0|0|1|0|>|0|0|_|_|-|1#0011", affichage=True)
    print("Accepte :", accepte)
    print("Ruban 3 final :", ruban3)


def demo_q10():
    ruban1, ruban2, ruban3, ruban4, accepte = machine_universelle_n_etapes("0|0|1|>|0|0|1|0|>|0|0|_|_|-|1#0011#5", affichage=True)
    print("Accepte :", accepte)
    print("Ruban 3 final :", ruban3)
    print("Ruban 4 final :", ruban4)


def demo_q11():
    print(preuves_q11())


def lancer_test(question):
    chemin = _chemin_test("test_" + question.upper() + ".py")
    runpy.run_path(str(chemin), run_name="__main__")


def main():
    commandes = {
        "q1": demo_q1,
        "q2": demo_q2,
        "q3": demo_q3,
        "q4": demo_q4,
        "q5": demo_q5,
        "q6": demo_q6,
        "q7": demo_q7,
        "q8": demo_q8,
        "q9": demo_q9,
        "q10": demo_q10,
        "q11": demo_q11,
    }

    if len(sys.argv) < 2:
        print("Utilisation : python3 projet.py q1|...|q11|test|test-q1|...|test-q11")
        return

    commande = sys.argv[1]

    if commande in commandes:
        commandes[commande]()
    elif commande == "test":
        for numero in range(1, 12):
            lancer_test("q" + str(numero))
    elif commande.startswith("test-q"):
        lancer_test(commande.replace("test-", ""))
    else:
        raise ValueError("Commande inconnue : " + commande)


if __name__ == "__main__":
    main()
