import json

print("--- CONFIGURACIÓN DE ACCESO UTP ---")
correo = input("Ingresa tu correo institucional (@utp.edu.pe): ").strip()
password = input("Ingresa tu contraseña de la UTP: ").strip()

datos = {
    "correo": correo,
    "password": password
}

with open("utp_credenciales.json", "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=2)

print("\n✅ Credenciales guardadas correctamente en utp_credenciales.json")