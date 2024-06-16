# Projekt - Dziennik

## 2024-05-26
1. Utworzenie pustej aplikacji Python+Flask.
2. Stworzenie AppService na platformie Azure.
3. Testowy deploy pustej aplikacji na Azure.
4. Dodanie bazy danych CosmosDb na platformie Azure.
5. Stworzenie przykładowego kontenera i jednego dokumentu.
6. Dodanie obsługi odczytu z bazy danych dokumentu i jego właściwości.
7. Dodanie .gitignore i wysłanie kodu na GitHub.

## 2024-05-27
1. Dodanie biblioteki bootstrap
2. Dodanie index.html z nagłówkiem, stopką i zawartością
3. Dodanie styli
4. Dodanie przycisku login, oraz szablonu login.html
5. Utworzenie formularza logowania w login.html. Dodanie styli
6. Utworzenie akcji (funkcji) login i zwrócenie szablonu login.html

## 2024-06-04
1. Dodanie okna rejestracji, modelu rejestracji, obsługa walidacji, zapis użytkownika do bazy
2. Aktualizacja okna logowania, obsługa logowania, zapis użytkownika w sesji.
3. Wyświetlenie profilu zalogowanego użytkownika w nagłówku
4. Dodanie i obsługa przycisku wylogowania.

## 2024-06-05
1. Dodanie pobierania podstawowych danych o geolokalizacji (koordynaty)
2. Dodanie biblioteki jQuery
3. Pobranie bieżących warunków pogodowych dla otrzymanych współrzędnych
4. Pobranie bieżących warunków jakości powietrza dla otrzymanych współrzędnych
5. Dodanie biblioteki Devextreme do wyświetlania danych za pomocą nowoczesnych kontrolek
6. Wyświetlenie indeksu jakości powietrza w bieżącej lokalizacji    

## 2024-06-14
1. Obsługa zmiany lokalizacji
    1. Dodanie inputa
    2. Wyszukiwanie koordynat dla wprowadzonej lokalizacji (miasto)
    3. Wyszukanie stanu jakości powietrza dla znalezionych koordynat
2. Obsługa powiadamiania - wyświetlanie checkboxa w zależności od informacji w bazie
3. Podstawowa obsługa wysyłania maila

## 2024-06-15
1. Obsługa powiadamiania
    1. Implementacja schedulera
    2. Wysyłka maila
    3. Impementacja logiki wysyłania maila 
        (przekroczenie wartości, nie częściej niż ustalony interwał, nie w nocy, użytkownik chce być powiadamiany)
2. Testowanie na środowisku lokalnym
3. Wdrożenie na platformę Azure
4. Testowanie na platformie Azure

## 2024-06-16
1. Dodanie FastApi
2. Implementacja endpointu autoryzacji
3. Implementacja endpointu /air zwracającego aktualny stan powietrza w wybranym mieście
4. Podstawowe wyczyszczenie aplikacji
5. Poprawienie stylowania błędów formularza
6. Dodanie walidatorów