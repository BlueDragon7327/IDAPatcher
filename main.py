"""IDAPatcher - simple command line helper."""

from pathlib import Path
import os
import ssl
import sys
import urllib.error
import urllib.request


def print_title() -> None:
	print()
	print(r"  ___ ____    _    ____       _       _               ")
	print(r" |_ _|  _ \  / \  |  _ \ __ _| |_ ___| |__   ___ _ __ ")
	print(r"  | || | | |/ _ \ | |_) / _` | __/ __| '_ \ / _ \ '__|")
	print(r"  | || |_| / ___ \|  __/ (_| | || (__| | | |  __/ |   ")
	print(r" |___|____/_/   \_\_|   \__,_|\__\___|_| |_|\___|_|   ")
	print()


def clear_console() -> None:
	os.system("cls" if os.name == "nt" else "clear")


def _progress_hook(block_num: int, block_size: int, total_size: int) -> None:
	if total_size <= 0:
		# Unknown size: show bytes downloaded only.
		downloaded = block_num * block_size
		sys.stdout.write(f"\r    Downloaded: {downloaded // 1024} KB")
		sys.stdout.flush()
		return

	downloaded = min(block_num * block_size, total_size)
	percent = (downloaded / total_size) * 100
	sys.stdout.write(
		f"\r    Progress: {percent:6.2f}% ({downloaded // 1024} / {total_size // 1024} KB)"
	)
	sys.stdout.flush()


def _download_with_context(url: str, destination: Path, context: ssl.SSLContext | None) -> None:
	with urllib.request.urlopen(url, context=context) as response, open(destination, "wb") as output:
		total = response.length or 0
		chunk_size = 64 * 1024
		downloaded = 0
		while True:
			chunk = response.read(chunk_size)
			if not chunk:
				break
			output.write(chunk)
			downloaded += len(chunk)
			if total > 0:
				percent = (downloaded / total) * 100
				sys.stdout.write(
					f"\r    Progress: {percent:6.2f}% ({downloaded // 1024} / {total // 1024} KB)"
				)
			else:
				sys.stdout.write(f"\r    Downloaded: {downloaded // 1024} KB")
			sys.stdout.flush()
	print()


def _is_ssl_error(exc: Exception) -> bool:
	message = str(exc).lower()
	if "certificate" in message or "ssl" in message or "tls" in message:
		return True
	if isinstance(exc, (ssl.SSLError, ssl.SSLCertVerificationError)):
		return True
	if isinstance(exc, urllib.error.URLError) and isinstance(exc.reason, ssl.SSLError):
		return True
	return False


def download_file(url: str, destination: Path) -> None:
	try:
		_download_with_context(url, destination, context=None)
		return
	except Exception as exc:
		if not _is_ssl_error(exc):
			raise

	print("\n    [!] SSL certificate validation failed on this machine.")
	print("    [*] Retrying with legacy compatibility mode...")
	insecure_context = ssl._create_unverified_context()
	_download_with_context(url, destination, context=insecure_context)


def install_ida_pro_v9() -> None:
	print("\n[+] Install IDA Pro v9 selected.")
	url = "https://github.com/BlueDragon7327/IDAPatcher/releases/download/files/installer.exe"
	installer_path = Path.cwd() / "installer.exe"

	try:
		print(f"    Downloading installer to: {installer_path}")
		download_file(url, installer_path)
		print("    Download complete.")

		print("    Launching installer...")
		os.startfile(installer_path)
		print("    Installer started.")
	except Exception as exc:
		print(f"    [!] Install failed: {exc}")


def patch_ida() -> None:
	print("\n[+] Patch selected.")
	url = "https://github.com/BlueDragon7327/IDAPatcher/releases/download/files/patcher.exe"
	patcher_path = Path.cwd() / "patcher.exe"

	try:
		print(f"    Downloading patcher to: {patcher_path}")
		download_file(url, patcher_path)
		print("    Download complete.")

		print("    Launching patcher...")
		os.startfile(patcher_path)
		print("    Patcher started.")
	except Exception as exc:
		print(f"    [!] Patch failed: {exc}")


def show_menu() -> None:
	print("1. install IDA Pro v9")
	print("2. patch")
	print("3. exit")


def main() -> None:
	while True:
		clear_console()
		print_title()
		show_menu()
		choice = input("\nSelect an option: ").strip()

		if choice == "1":
			install_ida_pro_v9()
		elif choice == "2":
			patch_ida()
		elif choice == "3":
			print("\nGoodbye.")
			break
		else:
			print("\n[!] Invalid selection. Choose 1, 2, or 3.")

		input("\nPress Enter to continue...")
		print()


if __name__ == "__main__":
	main()
