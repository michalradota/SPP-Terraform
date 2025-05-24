# SPP_Terraform
## Spełnione zostały wymagania:

• 3.0 - Zaimplementować infrastrukturę jeden z aplikacji z poprzednich zajęć
jako IaC korzystając z języka terraform.

• +0.5 - Zaimplementować infrastrukturę z backendem stanu terraforma na
S3 oraz DynamoDB,

• +0.5 - Dodać automatycznym deployment w CI/CD korzystając z GitHuba lub Gitlaba.

## Lista  plików:

•  gitignore - pliki nie śledzone w repozytorium,

• .terraform.lock.hcl - plik blokady Terraform, zapewnia spójność wersji providerów,
• README.md - dokumentacja repozytorium,

• backend.tf - plik konfiguracyjny dla backendu Terraform (wskazuje na użycie backendu S3 i blokady w DynamoDB, co pozwala na zarządzanie stanem w chmurze i unikanie konfliktów),

• lambda_function.py - kod źródłowy AWS Lambda z pierwszych zajęć,

• main.tf - główny plik konfiguracyjny Terraform. Definicje zasobów takich jak instacje EC2, Lambda, SQS, SNS i DynamoDB.
