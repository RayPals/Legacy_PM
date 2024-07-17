import os
import sys
import urllib2
import zipfile
import sqlite3
import json
import shutil
import platform

class PackageManager:
    def __init__(self, install_dir, db_path):
        self.install_dir = install_dir
        self.db_path = db_path
        self.repo_url = None  # Will be set based on Windows version
        if not os.path.exists(install_dir):
            os.makedirs(install_dir)
        self._init_db()
        self._check_windows_version()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS packages
                              (name TEXT PRIMARY KEY, version TEXT, path TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS drivers
                              (name TEXT PRIMARY KEY, version TEXT, path TEXT)''')
            conn.commit()

    def _check_windows_version(self):
        system = platform.system()
        release = platform.release()
        version = platform.version()

        print(f"Operating System: {system}")
        print(f"Version: {version}")
        print(f"Release: {release}")

        if system != 'Windows':
            print("This script is designed to run on Windows.")
            sys.exit(1)

        # Define repository URLs for different Windows versions
        repo_urls = {
            'Windows 95': 'http://example.com/repository_windows_95.json',
            'Windows 98': 'http://example.com/repository_windows_98.json',
            'Windows ME': 'http://example.com/repository_windows_me.json',
            'Windows NT 4.0': 'http://example.com/repository_windows_nt_4.json',
            'Windows 2000': 'http://example.com/repository_windows_2000.json',
            'Windows XP': 'http://example.com/repository_windows_xp.json',
            'Windows XP 64-Bit': 'http://example.com/repository_windows_xp_64.json',
            'Windows Server 2003': 'http://example.com/repository_windows_server_2003.json',
            'Windows Vista': 'http://example.com/repository_windows_vista.json',
            'Windows 7': 'http://example.com/repository_windows_7.json',
            'Windows 8': 'http://example.com/repository_windows_8.json',
            'Windows 8.1': 'http://example.com/repository_windows_8_1.json',
            'Windows 10': 'http://example.com/repository_windows_10.json',
            'Windows 11': 'http://example.com/repository_windows_11.json'
        }

        # Determine the version of Windows
        if '95' in release:
            print("Running on Windows 95.")
            self.repo_url = repo_urls['Windows 95']
        elif '98' in release:
            print("Running on Windows 98.")
            self.repo_url = repo_urls['Windows 98']
        elif 'ME' in release:
            print("Running on Windows ME.")
            self.repo_url = repo_urls['Windows ME']
        elif 'NT' in release:
            if '4.0' in version:
                print("Running on Windows NT 4.0.")
                self.repo_url = repo_urls['Windows NT 4.0']
            elif '5.0' in version:
                print("Running on Windows 2000.")
                self.repo_url = repo_urls['Windows 2000']
            elif '5.1' in version:
                print("Running on Windows XP.")
                self.repo_url = repo_urls['Windows XP']
            elif '5.2' in version:
                print("Running on Windows XP 64-Bit Edition or Windows Server 2003.")
                self.repo_url = repo_urls['Windows XP 64-Bit']  # Adjust based on actual detection logic
            elif '6.0' in version:
                print("Running on Windows Vista or Windows Server 2008.")
                self.repo_url = repo_urls['Windows Vista']
            elif '6.1' in version:
                print("Running on Windows 7 or Windows Server 2008 R2.")
                self.repo_url = repo_urls['Windows 7']
            elif '6.2' in version:
                print("Running on Windows 8 or Windows Server 2012.")
                self.repo_url = repo_urls['Windows 8']
            elif '6.3' in version:
                print("Running on Windows 8.1 or Windows Server 2012 R2.")
                self.repo_url = repo_urls['Windows 8.1']
            elif '10.0' in version:
                print("Running on Windows 10.")
                self.repo_url = repo_urls['Windows 10']
            elif '10.0' in version and '22000' in version:
                print("Running on Windows 11.")
                self.repo_url = repo_urls['Windows 11']
            else:
                print("Running on an unknown version of Windows NT.")
        else:
            print("Running on an unknown version of Windows.")

    def _add_package_to_db(self, name, version, path, table='packages'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO {} (name, version, path) VALUES (?, ?, ?)".format(table),
                           (name, version, path))
            conn.commit()

    def _remove_package_from_db(self, name, table='packages'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM {} WHERE name = ?".format(table), (name,))
            conn.commit()

    def _get_package_from_db(self, name, table='packages'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, version, path FROM {} WHERE name = ?".format(table), (name,))
            return cursor.fetchone()

    def _list_packages_from_db(self, table='packages'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, version, path FROM {}".format(table))
            return cursor.fetchall()

    def fetch_repository(self):
        response = urllib2.urlopen(self.repo_url)
        data = response.read()
        return json.loads(data)

    def find_package_in_repo(self, package_name, repo_data, type='packages'):
        for package in repo_data[type]:
            if package["name"] == package_name:
                return package
        return None

    def download_package(self, url):
        package_name = url.split('/')[-1]
        local_path = os.path.join(self.install_dir, package_name)
        print("Downloading package:", package_name)
        response = urllib2.urlopen(url)
        with open(local_path, 'wb') as f:
            f.write(response.read())
        print("Downloaded to:", local_path)
        return local_path

    def install_package(self, package_path, package_name, package_version, table='packages'):
        if package_path.endswith('.zip'):
            print("Installing package from:", package_path)
            with zipfile.ZipFile(package_path, 'r') as zip_ref:
                zip_ref.extractall(self.install_dir)
                extracted_path = os.path.join(self.install_dir, zip_ref.namelist()[0])
                self._add_package_to_db(package_name, package_version, extracted_path, table)
            print(f"Package {package_name} installed at:", self.install_dir)
        else:
            print("Unsupported package format:", package_path)

    def list_installed_packages(self):
        print("Installed packages:")
        packages = self._list_packages_from_db()
        for package in packages:
            print(f"- {package[0]} (version: {package[1]}, path: {package[2]})")

    def list_drivers(self):
        repo_data = self.fetch_repository()
        installed_drivers = {driver[0]: driver for driver in self._list_packages_from_db('drivers')}
        print("Drivers:")
        for driver in repo_data['drivers']:
            name = driver['name']
            if name in installed_drivers:
                installed_version = installed_drivers[name][1]
                print(f"- {name} (Installed version: {installed_version}, Available version: {driver['version']})")
            else:
                print(f"- {name} (Not installed, Available version: {driver['version']})")

    def remove_package(self, package_name, table='packages'):
        package_info = self._get_package_from_db(package_name, table)
        if package_info:
            package_path = package_info[2]
            if os.path.exists(package_path):
                shutil.rmtree(package_path)
                self._remove_package_from_db(package_name, table)
                print("Package removed:", package_name)
            else:
                print("Package not found:", package_name)
        else:
            print("Package not found:", package_name)

    def update_all_packages(self):
        repo_data = self.fetch_repository()
        installed_packages = self._list_packages_from_db()
        for installed_package in installed_packages:
            name, current_version, path = installed_package
            repo_package = self.find_package_in_repo(name, repo_data)
            if repo_package and repo_package["version"] != current_version:
                print(f"Updating package: {name}")
                self.remove_package(name)
                new_package_path = self.download_package(repo_package["url"])
                self.install_package(new_package_path, name, repo_package["version"])
                print(f"Package {name} updated to version {repo_package['version']}")

    def update_missing_drivers(self):
        repo_data = self.fetch_repository()
        installed_drivers = {driver[0]: driver for driver in self._list_packages_from_db('drivers')}
        for driver in repo_data['drivers']:
            name = driver['name']
            if name not in installed_drivers:
                print(f"Installing missing driver: {name}")
                driver_path = self.download_package(driver['url'])
                self.install_package(driver_path, name, driver['version'], 'drivers')
                print(f"Driver {name} installed")

def main():
    if len(sys.argv) < 2:
        print("Usage: python package_manager.py <command> [<args>]")
        return

    command = sys.argv[1]
    pm = PackageManager('packages', 'packages.db')

    if command == 'install':
        if len(sys.argv) < 3:
            print("Usage: python package_manager.py install <package_name>")
            return
        package_name = sys.argv[2]
        repo_data = pm.fetch_repository()
        package_in_repo = pm.find_package_in_repo(package_name, repo_data)
        if package_in_repo:
            package_url = package_in_repo["url"]
            package_version = package_in_repo["version"]
            package_path = pm.download_package(package_url)
            pm.install_package(package_path, package_name, package_version)
        else:
            print(f"Package {package_name} not found in repository")

    elif command == 'list':
        pm.list_installed_packages()

    elif command == 'remove':
        if len(sys.argv) < 3:
            print("Usage: python package_manager.py remove <package_name>")
            return
        package_name = sys.argv[2]
        pm.remove_package(package_name)

    elif command == 'update':
        pm.update_all_packages()

    elif command == 'driverlist':
        pm.list_drivers()

    elif command == 'driverupdate':
        pm.update_missing_drivers()

    else:
        print("Unknown command:", command)

if __name__ == '__main__':
    main()

