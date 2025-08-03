import pandas as pd
import numpy as np
import os, joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
from imblearn.combine import SMOTETomek
import warnings
warnings.filterwarnings('ignore')

print(" DÜZELTILMIŞ MİGREN TAHMİN MODELİ V7")
print("=" * 50)

def safe_feature_engineering(df):
    """Güvenli feature engineering - boyut uyumsuzluğunu önler"""
    df_eng = df.copy()
    
    # 1. Interaction features
    df_eng['stres_uyku_ratio'] = df_eng['Stres_Seviyesi'] / (df_eng['Uyku_Saati'] + 0.1)
    df_eng['ekran_su_ratio'] = df_eng['Ekran_Suresi_Saat'] / (df_eng['Su_Tuketimi_L'] + 0.1)
    df_eng['ruh_hali_uyku'] = df_eng['Ruh_Hali'] * df_eng['Uyku_Saati']
    
    # 2. Risk kategorileri
    df_eng['uyku_kategori'] = pd.cut(df_eng['Uyku_Saati'], 
                                    bins=[0, 6, 8, 12], 
                                    labels=[2, 1, 0])  # 2=kötü, 1=orta, 0=iyi
    
    df_eng['stres_kategori'] = pd.cut(df_eng['Stres_Seviyesi'], 
                                     bins=[0, 3, 7, 10], 
                                     labels=[0, 1, 2])  # 0=düşük, 1=orta, 2=yüksek
    
    # 3. Composite risk scores
    df_eng['lifestyle_risk'] = (
        (df_eng['Stres_Seviyesi'] / 10) * 0.3 +
        ((10 - df_eng['Uyku_Saati']) / 10) * 0.2 +
        (df_eng['Ekran_Suresi_Saat'] / 16) * 0.2 +
        ((5 - df_eng['Su_Tuketimi_L']) / 5) * 0.15 +
        ((5 - df_eng['Ruh_Hali']) / 5) * 0.15
    )
    
    # 4. Boolean features'ı sayısal yap
    df_eng['Parlak_Isik'] = df_eng['Parlak_Isik'].astype(int)
    df_eng['Beslenme_Duzensizligi'] = df_eng['Beslenme_Duzensizligi'].astype(int)
    df_eng['Hava_Degisimi'] = df_eng['Hava_Degisimi'].astype(int)
    
    # 5. Kategorik değişkenleri sayısal yap
    df_eng['uyku_kategori'] = df_eng['uyku_kategori'].astype(int)
    df_eng['stres_kategori'] = df_eng['stres_kategori'].astype(int)
    
    return df_eng

def intelligent_data_balancing(X, y, strategy='moderate'):
    """Akıllı veri dengeleme - aşırı örnekleme yapmadan"""
    print(f" Intelligent Data Balancing ({strategy})")
    print("=" * 35)
    
    # Mevcut dağılımı göster
    unique, counts = np.unique(y, return_counts=True)
    print("Mevcut dağılım:", dict(zip(unique, counts)))
    
    if strategy == 'moderate':
        # Orta seviye dengeleme - sadece çok az olanları artır
        sampling_strategy = {
            6: min(150, counts[unique == 6][0] * 2) if 6 in unique else 150,
            7: min(150, counts[unique == 7][0] * 2) if 7 in unique else 150,
            8: min(120, counts[unique == 8][0] * 3) if 8 in unique else 120,
            9: min(120, counts[unique == 9][0] * 3) if 9 in unique else 120,
        }
    else:  # conservative
        # Minimum dengeleme
        sampling_strategy = {
            8: min(80, counts[unique == 8][0] * 2) if 8 in unique else 80,
            9: min(80, counts[unique == 9][0] * 2) if 9 in unique else 80,
        }
    
    try:
        # SMOTETomek kullan - daha iyi sonuçlar
        smote_tomek = SMOTETomek(
            smote=SMOTE(random_state=42, k_neighbors=3),
            random_state=42
        )
        
        # Sadece belirli sınıfları dengelemeye çalış
        smote = SMOTE(random_state=42, sampling_strategy=sampling_strategy, k_neighbors=2)
        X_balanced, y_balanced = smote.fit_resample(X, y)
        
        # Yeni dağılımı göster
        unique_new, counts_new = np.unique(y_balanced, return_counts=True)
        print("Yeni dağılım:", dict(zip(unique_new, counts_new)))
        
        return X_balanced, y_balanced
        
    except Exception as e:
        print(f" SMOTE hatası: {e}")
        print(" Orijinal veri kullanılıyor...")
        return X, y

def evaluate_models(X_train, X_test, y_train, y_test):
    """Birden fazla model dene ve karşılaştır"""
    
    models = {
        'RandomForest': RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=20,
            min_samples_leaf=10,
            class_weight='balanced',
            random_state=42
        ),
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=150,
            max_depth=10,
            learning_rate=0.1,
            random_state=42
        )
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n {name} eğitiliyor...")
        
        # Cross-validation
        cv_scores = cross_val_score(
            model, X_train, y_train, 
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
            scoring='f1_weighted'
        )
        
        # Model eğit
        model.fit(X_train, y_train)
        
        # Test predictions
        y_pred = model.predict(X_test)
        test_accuracy = accuracy_score(y_test, y_pred)
        
        results[name] = {
            'model': model,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'test_accuracy': test_accuracy,
            'predictions': y_pred
        }
        
        print(f"   CV F1-Score: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
        print(f"   Test Accuracy: {test_accuracy:.3f}")
    
    return results

def main():
    try:
        # 1. Veri yükle
        print(" Veri yükleniyor...")
        train_df = pd.read_csv('migren_data_train.csv')
        test_df = pd.read_csv('migren_data_test.csv')
        
        print(f"   Eğitim: {len(train_df)} örnek")
        print(f"   Test: {len(test_df)} örnek")
        
        # 2. Feature columns tanımla
        feature_cols = ['Uyku_Saati', 'Stres_Seviyesi', 'Su_Tuketimi_L',
                       'Ekran_Suresi_Saat', 'Ruh_Hali', 'Parlak_Isik',
                       'Beslenme_Duzensizligi', 'Hava_Degisimi']
        
        # 3. Veriyi hazırla
        X_train_raw = train_df[feature_cols].copy()
        y_train = train_df['Migren_Riski'].copy()
        X_test_raw = test_df[feature_cols].copy()
        y_test = test_df['Migren_Riski'].copy()
        
        # 4. Feature Engineering
        print("\n Feature Engineering...")
        X_train_eng = safe_feature_engineering(X_train_raw)
        X_test_eng = safe_feature_engineering(X_test_raw)
        
        print(f"   Özellik sayısı: {len(feature_cols)} → {X_train_eng.shape[1]}")
        
        # 5. Scaling
        print("\n Feature Scaling...")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train_eng)
        X_test_scaled = scaler.transform(X_test_eng)
        
        # 6. Data Balancing
        print("\n Data Balancing...")
        X_train_balanced, y_train_balanced = intelligent_data_balancing(
            X_train_scaled, y_train, strategy='conservative'
        )
        
        # 7. Model Evaluation
        print("\n Model Eğitimi ve Değerlendirmesi")
        print("=" * 40)
        
        results = evaluate_models(
            X_train_balanced, X_test_scaled, 
            y_train_balanced, y_test
        )
        
        # 8. En iyi modeli seç
        best_model_name = max(results.keys(), 
                             key=lambda x: results[x]['test_accuracy'])
        best_result = results[best_model_name]
        
        print(f"\n EN İYİ MODEL: {best_model_name}")
        print("=" * 30)
        print(f"Test Accuracy: {best_result['test_accuracy']:.3f}")
        print(f"CV F1-Score: {best_result['cv_mean']:.3f}")
        
        # 9. Detaylı sonuçlar
        print(f"\n DETAYLI SONUÇLAR ({best_model_name})")
        print("=" * 35)
        print(classification_report(y_test, best_result['predictions']))
        
        # 10. Feature Importance
        if hasattr(best_result['model'], 'feature_importances_'):
            print("\n ÖNEMLİ ÖZELLİKLER")
            print("=" * 25)
            importances = best_result['model'].feature_importances_
            feature_names = X_train_eng.columns
            
            # Top 10 önemli özellik
            indices = np.argsort(importances)[::-1][:10]
            for i, idx in enumerate(indices, 1):
                print(f"{i:2d}. {feature_names[idx]:<20}: {importances[idx]:.3f}")
        
        print("\n Model eğitimi başarıyla tamamlandı!")

        # 10.1 Model ve scaler'ı kaydet

        save_dir = "ml_models/models"
        os.makedirs(save_dir, exist_ok=True)
        joblib.dump(best_result['model'], os.path.join(save_dir, "migraine_model.pkl"))
        joblib.dump(scaler, os.path.join(save_dir, "scaler.pkl"))
        print(f"\n Model ve scaler '{save_dir}' klasörüne kaydedildi!")

        return best_result['model'], scaler
        
    except FileNotFoundError as e:
        print(f" Dosya bulunamadı: {e}")
        print(" Lütfen CSV dosyalarının mevcut dizinde olduğundan emin olun.")
    except Exception as e:
        print(f" Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    model, scaler = main()
