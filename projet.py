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
        symboles_lus = [] #iniatialisation de la liste des symboles lus, si la machine a plusieurs rubans, on lira un symbole sur chaque ruban et on les stockera dans cette liste
        for i in range(machine.nb_rubans):  #pour chauque ruban
            position = config.positions[i]  #position de la tete de lecture sur le ruban i
            ruban = config.rubans[i] #pour le ruban i

            if position < 0:    #si la position est négative, on ajoute un blanc au début du ruban et on remet la position à 0
                ruban.insert(0, machine.blanc)
                config.positions[i] = 0
                position = 0

            if position >= len(ruban):  #si la position dépasse la longueur du ruban, on ajoute un blanc à la fin du ruban
                ruban.append(machine.blanc)

            symboles_lus.append(ruban[position])    #on ajoute le symbole lu à la liste des symboles lus

        if machine.nb_rubans == 1:      #si la machine a un seul ruban, on utilise une clé simple pour les transitions
            cle = (config.etat, symboles_lus[0])    #la cle est un tuple composé de l'état courant, et du symbole que l'on lit
        else:
            cle = (config.etat, tuple(symboles_lus))    #si la machine a plusieurs rubans, on utilise une clé composée de l'état courant et d'un tuple des symboles lus sur chaque ruban

        if cle not in machine.transitions:  #si la clé n'est pas dans les transitions de la machine, cela signifie que la machine est bloquée et ne peut pas continuer, on retourne None pour indiquer ce blocage
            return None

        nouvel_etat, symboles_ecrits, directions = machine.transitions[cle]    #si la clé est dans les transitions, on récupère le nouvel état, les symboles à écrire et les directions à suivre pour chaque ruban

        if machine.nb_rubans == 1: 
            symboles_ecrits = [symboles_ecrits] 
            directions = [directions]

        for i in range(machine.nb_rubans):  #pour chaque ruban i,
            position = config.positions[i]  #on récupère la position de la tête de lecture sur le ruban i
            ruban = config.rubans[i]    #on récupère le ruban i
            ruban[position] = symboles_ecrits[i]   #on écrit le symbole correspondant à ce ruban i à la position de la tête de lecture

        config.etat = nouvel_etat

        for i in range(machine.nb_rubans):  #pour chaque ruban i,
            direction = directions[i]   #On recupere la direction à suivre pour le ruban i

            if direction in ('R', '>'): #si la direction est à droite,
                config.positions[i] += 1    #on incrémente la position de la tête de lecture sur le ruban i
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
        """Selon le format de la machine dans le fichier texte, on lit les lignes du fichier et on construit la machine de Turing correspondante
        le format est le suivant :
        name: nom_de_la_machine (optionnel)
        init: etat_initial
        accept: etat_acceptant
        etat_source, symbole_lu1, symbole_lu2, ...
        etat_destination, symbole_ecrit1, symbole_ecrit2, ..., direction1, direction2, ...
        """
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

            if ligne.startswith("name:"):   #si la ligne commence par "name:", on ignore cette ligne et on passe à la suivante
                i += 1

            elif ligne.startswith("init:"):
                etat_initial = ligne.split(":", 1)[1].strip()   #si la ligne commence par "init:", on récupère l'état initial
                i += 1

            elif ligne.startswith("accept:"):   #si la ligne commence par "accept:", on récupère l'état acceptant
                etat_acceptant = ligne.split(":", 1)[1].strip()
                i += 1

            else:   #si la ligne ne commence par rien ci-dessus, c'est que c'est une transition
                condition = lignes[i]   #la condition de la transition est sur la ligne i, et l'instruction de la transition est sur la ligne i+1
                instruction = lignes[i + 1]
                morceaux_condition = [m.strip() for m in condition.split(',')]  #on decoupe la condition en morceaux, le premier morceau est l'état source, les suivants sont les symboles lus sur chaque ruban
                morceaux_instruction = [m.strip() for m in instruction.split(',')]  #on decoupe l'instruction en morceaux, le premier morceau est l'état destination, les suivants sont les symboles à écrire sur chaque ruban, puis les directions à suivre pour chaque ruban

                etat_source = morceaux_condition[0]
                symboles_lus = morceaux_condition[1:]

                etat_destination = morceaux_instruction[0]
                reste_instruction = morceaux_instruction[1:]

                nb_rubans = len(symboles_lus)

                symboles_ecrits = reste_instruction[:nb_rubans]
                directions = reste_instruction[nb_rubans:]

                if nb_rubans == 1:
                    cle = (etat_source, symboles_lus[0]) #si il n'y a qu'un seul ruban, il n'y a qu'un symbole dans symbole lus
                    valeur = (etat_destination, symboles_ecrits[0], directions[0])  #pareil pour les symboles écrits et les directions
                    alphabet.add(symboles_lus[0])   #on ajoute le symbole lu à l'alphabet de la machine
                    alphabet.add(symboles_ecrits[0])   #on ajoute le symbole écrit à l'alphabet de la machine
                else:
                    cle = (etat_source, tuple(symboles_lus))
                    valeur = (etat_destination, tuple(symboles_ecrits), tuple(directions))
                    for symbole in symboles_lus:
                        alphabet.add(symbole)
                    for symbole in symboles_ecrits:
                        alphabet.add(symbole)

                transitions[cle] = valeur   #on ajoute la transition dans le dictionnaire des transitions de la machine
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


def simuler_mot(mot, machine):
        config = configuration_initiale(mot, machine)
        nb_etapes = 0

        while config.etat != machine.etat_acceptant :
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
            '>': '110',
            'L': '100',
            'S': '101',
            'R': '110'
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

def decoder_machine_code(code_machine):
        morceaux = code_machine.split('|')

        if len(morceaux) % 5 != 0:
            raise ValueError("Le code de la machine est invalide.")

        transitions = {}
        alphabet = set()
        blanc = '_'

        for i in range(0, len(morceaux), 5):
            etat_source = morceaux[i]
            symbole_lu = morceaux[i + 1]
            symbole_ecrit = morceaux[i + 2]
            direction = morceaux[i + 3]
            etat_destination = morceaux[i + 4]

            transitions[(etat_source, symbole_lu)] = (etat_destination, symbole_ecrit, direction)
            alphabet.add(symbole_lu)
            alphabet.add(symbole_ecrit)

        return Machine_turing(alphabet, transitions, '0', '1', blanc, 1)


def ruban_avec_tete(ruban, position):
        ruban_marque = []

        for i in range(len(ruban)):
            symbole = ruban[i]
            if i == position:
                ruban_marque.append(symbole + '*')
            else:
                ruban_marque.append(symbole)

        return ' '.join(ruban_marque)


def afficher_rubans_universelle(ruban1, ruban2, ruban3, etape, ruban4=None):
    print(f"Etape {etape} :")
    print("Ruban 1 :", ruban1)
    print("Ruban 2 :", ruban2)
    print("Ruban 3 :", ruban3)
    if ruban4 is not None:
        print("Ruban 4 :", ruban4)
    print()


def machine_universelle(entree, affichage=False):
    code_machine, mot = entree.split('#', 1)
    machine = decoder_machine_code(code_machine)
    config = configuration_initiale(mot, machine)

    ruban1 = entree
    ruban2 = code_machine + '#' + config.etat
    ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])
    nb_etapes = 0

    if affichage:
        afficher_rubans_universelle(ruban1, ruban2, ruban3, nb_etapes)

    while config.etat != machine.etat_acceptant:
        nouvelle_config = un_pas(machine, config)

        if nouvelle_config is None:
            ruban2 = code_machine + '#blocage'
            ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])

            if affichage:
                afficher_rubans_universelle(ruban1, ruban2, ruban3, nb_etapes)

            return ruban1, ruban2, ruban3, False

        config = nouvelle_config
        nb_etapes += 1

        ruban2 = code_machine + '#' + config.etat
        ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])

        if affichage:
            afficher_rubans_universelle(ruban1, ruban2, ruban3, nb_etapes)

    accepte = config.etat == machine.etat_acceptant
    return ruban1, ruban2, ruban3, accepte


def machine_universelle_n_etapes(entree, affichage=False):
    parties = entree.split('#')

    code_machine, mot, etape = parties
    machine = decoder_machine_code(code_machine)
    config = configuration_initiale(mot, machine)
    compteur_restant = int(etape)

    ruban1 = entree
    ruban2 = code_machine + '#' + config.etat
    ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])
    ruban4 = '1' * compteur_restant + '_'
    nb_etapes = 0

    if affichage:
        afficher_rubans_universelle(ruban1, ruban2, ruban3, nb_etapes, ruban4)

    while config.etat != machine.etat_acceptant and compteur_restant > 0:
        nouvelle_config = un_pas(machine, config)

        if nouvelle_config is None:
            ruban2 = code_machine + '#blocage'
            ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])
            ruban4 = '1' * compteur_restant + '_'

            if affichage:
                afficher_rubans_universelle(ruban1, ruban2, ruban3, nb_etapes, ruban4)

            return ruban1, ruban2, ruban3, ruban4, False

        config = nouvelle_config
        nb_etapes += 1
        compteur_restant -= 1

        ruban2 = code_machine + '#' + config.etat
        ruban3 = ruban_avec_tete(config.rubans[0], config.positions[0])
        ruban4 = '1' * compteur_restant + '_'

        if affichage:
            afficher_rubans_universelle(ruban1, ruban2, ruban3, nb_etapes, ruban4)

    accepte = config.etat == machine.etat_acceptant
    return ruban1, ruban2, ruban3, ruban4, accepte
