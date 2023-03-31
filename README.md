# Graduation-Project-2022
Turkish Text Classification


Projede Python diliyle yazılan programda veri setlerine göre eğitilip oluşturulan
modellerle Türkçe metinler üzerinde sınıflandırma çalışılması yapılmıştır. Öncelikle programa
gönderilen Türkçe metinler Java diliyle yazılan Zemberek kütüphanesi ile ön işleme tabii
tutulup stopword’lerden arındırılarak incelenmeye hazır hale getirilmiştir. Ön işlenen metinler
TF-IDF yöntemi ile hazırlanan ve sonrasında güncel metinler için elle güncellenen kelime
listelerine göre sayısal vektörlere çevrilip arff formatında yazıldıktan sonra Weka yazılımı
aracılığıyla on farklı temel makine öğrenme algoritmalarıyla modeller kullanılarak önceden
belirlenmiş dört kategorinin kombinasyonlarına (astroloji, ekonomi, siyaset, spor) göre hangi
sınıflara girecekleri tespit edilmiştir.
