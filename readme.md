Opis projektu

Celem projektu jest wykorzystanie narzędzi DevOps w praktyce poprzez stworzenie i zarządzanie aplikacją webową. Projekt obejmuje kluczowe aspekty zarządzania kodem źródłowym, konteneryzacji aplikacji oraz procesu CI.

Instrukcja instalacji

Klonowanie repozytorium:

git clone https://github.com/Gringee/DevOps_Project/
cd DevOps_Project-master

Instalacja zależności:
Upewnij się, że masz zainstalowanego Dockera. Zbuduj obraz Dockera:

docker build -t devops_project .

Uruchomienie aplikacji:

docker run -p 5000:5000 devops_project

Aplikacja będzie dostępna pod adresem: http://localhost:5000
