{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "e401d760-a850-4400-9c12-036d89b32830",
   "metadata": {},
   "outputs": [
    {
     "name": "stdin",
     "output_type": "stream",
     "text": [
      "Enter value to encrypt (e.g., password):  Alok@51645424\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "🔐 Encrypted value (copy this for .env):\n",
      "gAAAAABoALJ9wRC_E-XOx5nS3R32WEsPQs-N_Q9Ssx_NtOu_3MHSiF_kYTPB-v37CRhznBniXzkxxaRv99u6Iv_R29AQ6by-0w==\n"
     ]
    }
   ],
   "source": [
    "from cryptography.fernet import Fernet\n",
    "\n",
    "# Paste your Fernet key here\n",
    "fernet_key = b'G27cB-481MjcPaF_YjXjuSrOGDJBHNczx6mP-J7O_b4='  # NOTE: keep the `b''` around the key\n",
    "fernet = Fernet(fernet_key)\n",
    "\n",
    "# The plain text value you want to encrypt\n",
    "plain_text = input(\"Enter value to encrypt (e.g., password): \").strip()\n",
    "encrypted = fernet.encrypt(plain_text.encode())\n",
    "print(\"\\n🔐 Encrypted value (copy this for .env):\")\n",
    "print(encrypted.decode())\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.1"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
