# credstuff
---
#### We found a leak of a blackmarket website's login credentials. Can you find the password of the user cultiris and successfully decrypt it? Download the leak here. The first user in usernames.txt corresponds to the first password in passwords.txt. The second user corresponds to the second password, and so on.

---
Giải nén file ra thì được 2 file txt gồm username và password.
Đề bảo ta tìm cultiris và username dòng thứ i thì password cũng ở dòng i, ở đây là dòng 378.
Khi đó ta tìm được password cvpbPGS{P7e1S_54I35_71Z3}. Format này rất quen, giống bài 13 chúng ta đã làm vậy nên suy đoán là ROT13 để giải.
```flag: picoCTF{C7r1F_54V35_71M3}```
