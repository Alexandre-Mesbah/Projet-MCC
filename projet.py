class Machine_turing :
    def __init__(self, alphabet, transitions, etat_initial, etat_acceptant, blanc, nb_rubans):
        self.alphabet = alphabet
        self.transitions = transitions
        self.etat_initial = etat_initial
        self.etat_acceptant = etat_acceptant
        self.blanc = blanc
        self.nb_rubans = nb_rubans


class Configuration :
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
        ruban = config.rubans[i]
        ruban[position] = symboles_ecrits[i]

    config.etat = nouvel_etat

    for i in range(machine.nb_rubans):
        direction = directions[i]

        if direction in ('R', '>'):
            config.positions[i] += 1
        elif direction in ('L', '<'):
            config.positions[i] -= 1

            if config.positions[i] < 0:
                config.rubans[i].insert(0, machine.blanc)
                config.positions[i] = 0
        elif direction in ('S', '-'):
            pass

        if config.positions[i] >= len(config.rubans[i]):
            config.rubans[i].append(machine.blanc)

    return config


def lire_machine(chemin_fichier):
    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        lignes = [ligne.strip() for ligne in f if ligne.strip()]

    etat_initial = None
    etat_acceptant = None
    transitions = {}
    alphabet = set()
    blanc = '_'
    nb_rubans = 1

    i = 0
    while i < len(lignes):
        ligne = lignes[i]

        if ligne.startswith("name:"):
            i += 1

        elif ligne.startswith("init:"):
            etat_initial = ligne.split(":", 1)[1].strip()
            i += 1

        elif ligne.startswith("accept:"):
            etat_acceptant = ligne.split(":", 1)[1].strip()
            i += 1

        else:
            condition = lignes[i]
            instruction = lignes[i + 1]

            etat_source, symbole_lu = condition.split(',')
            etat_destination, symbole_ecrit, direction = instruction.split(',')

            transitions[(etat_source, symbole_lu)] = (etat_destination, symbole_ecrit, direction)

            alphabet.add(symbole_lu)
            alphabet.add(symbole_ecrit)

            i += 2

    return Machine_turing(alphabet, transitions, etat_initial, etat_acceptant, blanc, nb_rubans)



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
    etat = machine.etat_initial
    return Configuration(rubans, positions, etat)


def simuler_mot(mot, machine, max_etapes=1000):
    config = configuration_initiale(mot, machine)
    nb_etapes = 0

    while config.etat != machine.etat_acceptant and nb_etapes < max_etapes:
        nouvelle_config = un_pas(machine, config)

        if nouvelle_config is None:
            return config, False

        config = nouvelle_config
        nb_etapes += 1

    accepte = config.etat == machine.etat_acceptant
    return config, accepte


def afficher_configuration(config):
    print("Etat :", config.etat)

    for i in range(len(config.rubans)):
        ruban = ''.join(config.rubans[i])
        tete = ' ' * config.positions[i] + '^'
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

    accepte = config.etat == machine.etat_acceptant
    return config, accepte

def lire_machine2(chemin_fichier):
    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        lignes = [ligne.strip() for ligne in f if ligne.strip()]

    etat_initial = None
    etat_acceptant = None
    transitions = []

    i = 0
    while i < len(lignes):
        ligne = lignes[i]

        if ligne.startswith("name:"):
            i += 1

        elif ligne.startswith("init:"):
            etat_initial = ligne.split(":", 1)[1].strip()
            i += 1

        elif ligne.startswith("accept:"):
            etat_acceptant = ligne.split(":", 1)[1].strip()
            i += 1

        else:
            condition = lignes[i]
            instruction = lignes[i + 1]

            etat_source, symbole_lu = condition.split(',')
            etat_destination, symbole_ecrit, direction = instruction.split(',')
            transitions.append((etat_source, symbole_lu, symbole_ecrit, direction, etat_destination))

            i += 2

    codes_etats = {}
    codes_etats[etat_initial] = '0'
    codes_etats[etat_acceptant] = '1'

    prochain_code = 2
    for etat_source, _, _, _, etat_destination in transitions:
        if etat_source not in codes_etats:
            codes_etats[etat_source] = bin(prochain_code)[2:]
            prochain_code += 1
        if etat_destination not in codes_etats:
            codes_etats[etat_destination] = bin(prochain_code)[2:]
            prochain_code += 1

    morceaux = []
    for etat_source, symbole_lu, symbole_ecrit, direction, etat_destination in transitions:
        morceaux.extend([
            codes_etats[etat_source],
            symbole_lu,
            symbole_ecrit,
            direction,
            codes_etats[etat_destination]
        ])

    return '|'.join(morceaux)


def coder_binaire(chaine):
    codage_binaire = {
        '0': '000',
        '1': '001',
        '|': '010',
        '_': '011',
        '<': '100',
        '-': '101',
        '>': '110'
    }

    resultat = ''
    for caractere in chaine:
        resultat += codage_binaire[caractere]

    return resultat


def lire_machine_binaire(chemin_fichier):
    code_machine = lire_machine2(chemin_fichier)
    return coder_binaire(code_machine)


def convertie_binaire(chaine_binaire):
    return int(chaine_binaire, 2)
