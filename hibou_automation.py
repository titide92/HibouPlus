#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Améliore l'interface du site web Hibouthèque (gestion d'une bibliothèque élémentaire) en ajoutant une surcouche.
Améliore l'efficacité du prêt et du retour des livres.
"""

from logging import config
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

try:
    from pynput import keyboard
except ImportError:  # pragma: no cover - optional dependency for non-scanner environments
    keyboard = None

"""exemple of config.local:
url=https://v2.hiboutheque.fr
login=trucMuche
password=my_password!
mediatheque_id=1111-my-mediatheque-id
"""

def load_config(filename='config.local'):
    config = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config


class HibouAutomation:
    def __init__(self):
        config = load_config()
        self.driver = None
        self.wait = None
        self.base_url = config['url']
        self.login = config['login']
        self.password = config['password']
        self.mediatheque_id = config['mediatheque_id']

        # Variables pour la gestion du scanner
        self.scanner_input = ""
        self.listener = None
        self.is_running = True

    def start_browser(self):
        """Initialise le navigateur Selenium avec options optimisées"""
        print("🌐 Démarrage du navigateur...")
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            # Désactiver les notifications de sécurité
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")

            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 15)

            # Masquer les signes d'automatisation
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            print("✓ Navigateur démarré avec succès")
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du navigateur: {e}")
            print("💡 Solutions:")
            print("   - Vérifiez que Google Chrome est installé")
            print("   - Fermez toutes les instances de Chrome")
            print("   - Redémarrez votre ordinateur")
            raise

    def login_to_site(self):
        """Connexion au site Hibothèque avec gestion d'erreurs robuste"""
        print("🔐 Connexion au site...")
        try:
            self.driver.get(f"{self.base_url}/connexion")
            time.sleep(2)  # Attendre le chargement complet
            identifiant_field = password_field = connexion_button = None
            original_selectors_method = False   # disable original selectors method for now, as it seems to be the one causing issues on some sites. We can re-enable it later if needed.
            if original_selectors_method:   # Méthode 1: Sélecteurs originaux
                try:
                    print("  → Tentative avec sélecteurs originaux...")
                    identifiant_field = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Identifiant']"))
                    )
                    password_field = self.driver.find_element(By.XPATH, "//input[@aria-label='Mot de passe']")
                    connexion_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Connexion')]")
                    print("  ✓ Sélecteurs originaux trouvés")
                except (TimeoutException, NoSuchElementException):
                    print(f"❌ Erreur lors de la connexion (Méthode sélecteurs originaux)")

            # Méthode 2: Sélecteurs alternatifs
            # alternative_selectors_method = True
            if connexion_button is None:   # only try alternative selectors if original selectors method failed
                print("  → Tentative avec sélecteurs alternatifs...")
                try:
                    identifiant_field = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
                    )
                    password_field = self.driver.find_element(By.XPATH, "//input[@type='password']")
                    connexion_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                    print("  ✓ Sélecteurs alternatifs trouvés")
                except (TimeoutException, NoSuchElementException):
                    # Méthode 3: Recherche par placeholder
                    print("  → Tentative avec recherche par placeholder...")
                    identifiant_field = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Identifiant') or contains(@placeholder, 'identifiant')]"))
                    )
                    password_field = self.driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Mot de passe') or contains(@placeholder, 'mot de passe')]")
                    connexion_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Connexion') or contains(text(), 'connexion')]")
                    print("  ✓ Sélecteurs par placeholder trouvés")

            if not identifiant_field or not password_field or not connexion_button:
                print("  ❌ Impossible de trouver les éléments de connexion")
                return False

            # Remplir les champs
            print("  → Remplissage des champs...")
            identifiant_field.clear()
            identifiant_field.send_keys(self.login)
            time.sleep(0.5)

            password_field.clear()
            password_field.send_keys(self.password)
            time.sleep(0.5)

            # Cliquer sur connexion
            print("  → Clic sur le bouton Connexion...")
            connexion_button.click()

            # Attendre la redirection
            print("  → Attente de la redirection...")
            time.sleep(3)

            # Vérifier si la connexion a réussi
            current_url = self.driver.current_url
            if "mediatheques" in current_url or "Bienvenue" in self.driver.page_source:
                print("✓ Connexion réussie")
                return True
            else:
                print(f"⚠ URL actuelle: {current_url}")
                print("⚠ La connexion peut avoir échoué - vérifiez manuellement")
                return False

        except Exception as e:
            print(f"❌ Erreur lors de la connexion: {e}")
            print("💡 Solutions:")
            print("   - Vérifiez votre connexion Internet")
            print("   - Le site peut avoir changé")
            print("   - Essayez de vous connecter manuellement d'abord")
            return False

    def go_to_page(self, page_name, page_end_url, wait_title_xpath):
        """Navigation vers la page"""
        print(f"📄 Navigation vers la page de '{page_name}'...")
        try:
            url = f"{self.base_url}/mediatheque/{self.mediatheque_id}/{page_end_url}/"
            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.XPATH, wait_title_xpath)))
            print(f"✓ Page de '{page_name}' chargée")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la navigation vers '{page_name}': {e}")
            return False

    def go_to_pret_page(self):
        """Navigation vers la page de prêt/retour"""
        return self.go_to_page(
            page_name="prêt/retour",
            page_end_url="faire-un-pret-ou-un-retour",
            wait_title_xpath="//h1[contains(text(), 'Faire un prêt') or contains(text(), 'prêt')]"
        )

    def on_press(self, key):
        """Callback pour chaque touche pressée du scanner"""
        try:
            if hasattr(key, 'char') and key.char:
                self.scanner_input += key.char
            elif key == keyboard.Key.enter:
                if self.scanner_input.strip():
                    self._process_scanner_input()
                self.scanner_input = ""
        except Exception as e:
            print(f"⚠ Erreur lors de la capture du scanner: {e}")

    def _process_scanner_input(self):
        """Traite l'entrée du scanner"""
        try:
            scanner_data = self.scanner_input.strip()
            print(f"\n📖 Entrée scanner reçue: {scanner_data}")

            if scanner_data.startswith("%"):
                borrower_number = scanner_data[1:]
                self._fill_borrower_field(borrower_number)
            else:
                exemplaire_number = scanner_data.lstrip(".")
                self._fill_exemplaire_field(exemplaire_number)
        except Exception as e:
            print(f"❌ Erreur lors du traitement du scanner: {e}")

    def _fill_borrower_field(self, borrower_number):
        """Remplit le champ emprunteur avec gestion d'erreurs"""
        try:
            print(f"  → Remplissage du champ emprunteur: {borrower_number}")

            # Chercher le champ emprunteur
            borrower_field = None
            try:
                borrower_field = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Nom ou numéro d\\'emprunteur']"))
                )
            except:
                try:
                    borrower_field = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'emprunteur') or contains(@placeholder, 'Emprunteur')]"))
                    )
                except:
                    borrower_field = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "(//input[@type='text'])[1]"))
                    )

            borrower_field.click()
            time.sleep(0.3)
            borrower_field.clear()
            borrower_field.send_keys(borrower_number)
            time.sleep(0.8)

            # Attendre et cliquer sur suggestion
            try:
                options = self.wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//li[@role='option']"))
                )
                if options:
                    options[0].click()
                    time.sleep(0.3)
                    print("  ✓ Emprunteur sélectionné")
                else:
                    print("  ⚠ Aucune suggestion trouvée")
            except:
                print("  ⚠ Pas de suggestions trouvées")

        except Exception as e:
            print(f"  ❌ Erreur lors du remplissage du champ emprunteur: {e}")

    def _fill_exemplaire_field(self, exemplaire_number):
        """Remplit le champ exemplaire et valide le prêt"""
        try:
            print(f"  → Remplissage du champ exemplaire: {exemplaire_number}")

            # Chercher le champ exemplaire
            exemplaire_field = None
            try:
                exemplaire_field = self.driver.find_element(By.XPATH,
                    "//h2[contains(text(), 'Faire un prêt')]/ancestor::div//input[@aria-label='Numéro d\\'exemplaire']")
            except:
                try:
                    exemplaire_field = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "(//input[@aria-label='Numéro d\\'exemplaire'])[1]"))
                    )
                except:
                    exemplaire_field = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "(//input[contains(@placeholder, 'exemplaire') or contains(@placeholder, 'Exemplaire')])[1]"))
                    )

            exemplaire_field.click()
            time.sleep(0.2)
            exemplaire_field.clear()
            exemplaire_field.send_keys(exemplaire_number)
            time.sleep(0.3)

            # Cliquer sur le bouton Prêter
            pret_button = None
            try:
                pret_button = self.driver.find_element(By.XPATH,
                    "//h2[contains(text(), 'Faire un prêt')]/ancestor::div//button[contains(text(), 'Prêter')]")
            except:
                pret_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Prêter')]")

            pret_button.click()
            print("  ✓ Bouton Prêter cliqué")

            # Gérer la confirmation
            self._handle_confirmation()

        except Exception as e:
            print(f"  ❌ Erreur lors du remplissage du champ exemplaire: {e}")

    def _handle_confirmation(self):
        """Gère la page de confirmation"""
        try:
            print("  → Attente de la page de confirmation...")

            self.wait.until(EC.presence_of_element_located((By.XPATH,
                "//h1[contains(text(), 'Confirmation')] | //button[contains(text(), 'Ok')] | //button[contains(text(), 'OK')]")))

            time.sleep(1)

            ok_button = None
            try:
                ok_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Ok') or contains(text(), 'OK')]")
            except:
                ok_button = self.driver.find_element(By.XPATH, "//button[@type='submit' or @class='btn btn-primary']")

            ok_button.click()
            print("  ✓ Bouton Ok cliqué")

            self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Faire un prêt')]")))
            print("  ✓ Prêt validé - Prêt à accepter le prochain")

            time.sleep(0.5)

        except Exception as e:
            print(f"  ❌ Erreur lors de la confirmation: {e}")

    def start_scanner_listener(self):
        """Démarre l'écoute du scanner"""
        if keyboard is None:
            print("⚠ pynput n'est pas disponible, l'écoute du scanner est désactivée")
            return

        print("\n" + "="*60)
        print("🚀 ÉCOUTE DU SCANNER ACTIVÉE")
        print("="*60)
        print("📝 Format des scans:")
        print("   - Emprunteur: %<numéro> + Entrée")
        print("   - Exemplaire: <numéro> ou .<numéro> + Entrée")
        print("\n📋 Appuyez sur Ctrl+C pour arrêter")
        print("="*60 + "\n")

        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def prepare_for_operations(self):
        """Prépare le navigateur et la page de prêt/retour pour une exécution manuelle."""
        self.start_browser()
        if not self.login_to_site():
            raise RuntimeError("Échec de la connexion au site")
        if not self.go_to_pret_page():
            raise RuntimeError("Échec de la navigation vers la page de prêt/retour")

    def process_manual_entry(self, entry, action_label="opération"):
        """Traite une ligne saisie manuellement ou importée depuis une base."""
        entry = (entry or "").strip()
        if not entry:
            return False

        print(f"📌 {action_label}: {entry}")
        if entry.startswith("%"):
            borrower_number = entry[1:]
            self._fill_borrower_field(borrower_number)
        else:
            exemplaire_number = entry.lstrip(".")
            self._fill_exemplaire_field(exemplaire_number)
        return True

    def run(self):
        """Lance la séquence complète"""
        try:
            self.start_browser()

            if not self.login_to_site():
                print("❌ Échec de la connexion - arrêt du script")
                return

            if not self.go_to_pret_page():
                print("❌ Échec de navigation - arrêt du script")
                return

            self.start_scanner_listener()
            self.listener.join()

        except KeyboardInterrupt:
            print("\n\n⛔ Arrêt du script demandé par l'utilisateur...")
        except Exception as e:
            print(f"\n❌ Erreur critique: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()

    def cleanup(self):
        """Nettoie les ressources"""
        if self.listener:
            self.listener.stop()
        if self.driver:
            self.driver.quit()
        print("\n✓ Ressources libérées - Script arrêté")


def main():
    """Point d'entrée principal"""
    try:
        automation = HibouAutomation()
        automation.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Erreur fatale: {e}")
        exit(1)


if __name__ == "__main__":
    main()
