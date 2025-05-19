resource "aws_s3_bucket" "terraform_backend" {
  bucket = "twoj-unikalny-bucket-terraform-2025"

  tags = {
    Name        = "TerraformBackendBucket"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_versioning" "terraform_backend_versioning" {
  bucket = aws_s3_bucket.terraform_backend.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = "TerraformLocksTable"
    Environment = "Dev"
  }
}

terraform {
  backend "s3" {
    bucket         = "twoj-unikalny-bucket-terraform-2025"  # <- wpisz tutaj swoją nazwę bucketu
    key            = "terraform.tfstate"                     # klucz pliku stanu w bucketcie
    region         = "us-east-1"
    use_lockfile   = true                    # tabela do blokady stanu
    encrypt        = true                                    # szyfrowanie pliku stanu
  }
}
