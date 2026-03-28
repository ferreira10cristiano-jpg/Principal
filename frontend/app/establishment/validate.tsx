import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  TextInput,
  ScrollView,
  Platform,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { Camera, CameraView } from 'expo-camera';
import { api } from '../../src/lib/api';
import { useAuthStore } from '../../src/store/authStore';

export default function ValidateScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { refreshUser } = useAuthStore();
  const [codeInput, setCodeInput] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [scanned, setScanned] = useState(false);
  const [showScanner, setShowScanner] = useState(false);
  const [inputMode, setInputMode] = useState<'scanner' | 'manual'>('scanner');

  useEffect(() => {
    (async () => {
      try {
        const { status } = await Camera.requestCameraPermissionsAsync();
        setHasPermission(status === 'granted');
      } catch (error) {
        console.log('Camera permission error:', error);
        setHasPermission(false);
      }
    })();
  }, []);

  const handleBarCodeScanned = async ({ data }: { data: string }) => {
    if (scanned || isValidating) return;
    setScanned(true);
    await handleValidate(data);
  };

  const handleValidate = async (code: string) => {
    const codeToValidate = code.trim().toUpperCase();
    if (!codeToValidate) {
      Alert.alert('Erro', 'Digite ou escaneie o código');
      setScanned(false);
      return;
    }

    setIsValidating(true);
    setValidationResult(null);
    setShowScanner(false);

    try {
      const result = await api.validateQR(codeToValidate);
      setValidationResult(result);
      await refreshUser();
      setCodeInput('');
    } catch (error: any) {
      Alert.alert('Erro', error.message || 'Falha ao validar código');
      setScanned(false);
    } finally {
      setIsValidating(false);
    }
  };

  const resetValidation = () => {
    setValidationResult(null);
    setScanned(false);
    setCodeInput('');
  };

  return (
    <View style={[styles.container, { paddingTop: insets.top }]}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
        </TouchableOpacity>
        <Text style={styles.title}>Validar QR Code</Text>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        {validationResult ? (
          // Validation Result Screen
          <View style={styles.resultContainer}>
            <View style={styles.successIcon}>
              <Ionicons name="checkmark-circle" size={80} color="#10B981" />
            </View>
            <Text style={styles.successTitle}>Venda Validada com Sucesso!</Text>

            {/* Sale Details Card */}
            <View style={styles.saleCard}>
              <View style={styles.saleHeader}>
                <Ionicons name="receipt" size={24} color="#3B82F6" />
                <Text style={styles.saleHeaderTitle}>Detalhes da Venda</Text>
              </View>

              <View style={styles.saleRow}>
                <Text style={styles.saleLabel}>Cliente:</Text>
                <Text style={styles.saleValue}>{validationResult.customer_name}</Text>
              </View>

              <View style={styles.saleRow}>
                <Text style={styles.saleLabel}>Oferta:</Text>
                <Text style={styles.saleValue}>{validationResult.offer?.title || validationResult.sale?.offer_title}</Text>
              </View>

              <View style={styles.saleRow}>
                <Text style={styles.saleLabel}>Código:</Text>
                <Text style={styles.saleValueCode}>{validationResult.voucher?.backup_code || validationResult.sale?.backup_code}</Text>
              </View>

              <View style={styles.divider} />

              <View style={styles.saleRow}>
                <Text style={styles.saleLabel}>Preço com desconto:</Text>
                <Text style={styles.saleValue}>
                  R$ {(validationResult.discounted_price || validationResult.sale?.discounted_price || 0).toFixed(2).replace('.', ',')}
                </Text>
              </View>

              {/* Credits Used */}
              <View style={styles.creditsRow}>
                <View style={styles.creditsIcon}>
                  <Ionicons name="wallet" size={20} color="#3B82F6" />
                </View>
                <View style={styles.creditsInfo}>
                  <Text style={styles.creditsLabel}>Pago com Créditos:</Text>
                  <Text style={styles.creditsValue}>
                    R$ {(validationResult.credits_used || validationResult.sale?.credits_used || 0).toFixed(2).replace('.', ',')}
                  </Text>
                </View>
              </View>

              {/* Amount to Pay Cash */}
              <View style={styles.cashRow}>
                <View style={styles.cashIcon}>
                  <Ionicons name="cash" size={24} color="#10B981" />
                </View>
                <View style={styles.cashInfo}>
                  <Text style={styles.cashLabel}>VALOR RESTANTE A PAGAR:</Text>
                  <Text style={styles.cashValue}>
                    R$ {(validationResult.amount_to_pay_cash || validationResult.sale?.amount_to_pay_cash || 0).toFixed(2).replace('.', ',')}
                  </Text>
                </View>
              </View>
            </View>

            {/* Credits Added Info */}
            {(validationResult.credits_used > 0 || validationResult.sale?.credits_used > 0) && (
              <View style={styles.creditAddedInfo}>
                <Ionicons name="arrow-up-circle" size={20} color="#10B981" />
                <Text style={styles.creditAddedText}>
                  R$ {(validationResult.credits_used || validationResult.sale?.credits_used || 0).toFixed(2).replace('.', ',')} adicionados ao seu saldo para saque
                </Text>
              </View>
            )}

            <TouchableOpacity style={styles.newScanButton} onPress={resetValidation}>
              <Ionicons name="qr-code" size={20} color="#FFFFFF" />
              <Text style={styles.newScanButtonText}>Validar Outro Código</Text>
            </TouchableOpacity>
          </View>
        ) : (
          // Scanner/Input Screen
          <>
            {/* Mode Selector */}
            <View style={styles.modeSelector}>
              <TouchableOpacity
                style={[styles.modeButton, inputMode === 'scanner' && styles.modeButtonActive]}
                onPress={() => setInputMode('scanner')}
              >
                <Ionicons name="camera" size={20} color={inputMode === 'scanner' ? '#FFFFFF' : '#64748B'} />
                <Text style={[styles.modeButtonText, inputMode === 'scanner' && styles.modeButtonTextActive]}>
                  Câmera
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.modeButton, inputMode === 'manual' && styles.modeButtonActive]}
                onPress={() => setInputMode('manual')}
              >
                <Ionicons name="keypad" size={20} color={inputMode === 'manual' ? '#FFFFFF' : '#64748B'} />
                <Text style={[styles.modeButtonText, inputMode === 'manual' && styles.modeButtonTextActive]}>
                  Digitar
                </Text>
              </TouchableOpacity>
            </View>

            {inputMode === 'scanner' ? (
              // Camera Scanner
              <View style={styles.scannerContainer}>
                {hasPermission === null ? (
                  <View style={styles.permissionContainer}>
                    <ActivityIndicator size="large" color="#3B82F6" />
                    <Text style={styles.permissionText}>Verificando permissão da câmera...</Text>
                  </View>
                ) : hasPermission === false ? (
                  <View style={styles.permissionContainer}>
                    <Ionicons name="camera-outline" size={64} color="#EF4444" />
                    <Text style={styles.permissionTitle}>Câmera não disponível</Text>
                    <Text style={styles.permissionText}>
                      Use a opção "Digitar" para inserir o código manualmente
                    </Text>
                    <TouchableOpacity style={styles.manualButton} onPress={() => setInputMode('manual')}>
                      <Text style={styles.manualButtonText}>Digitar Código</Text>
                    </TouchableOpacity>
                  </View>
                ) : (
                  <View style={styles.cameraContainer}>
                    <CameraView
                      style={styles.camera}
                      facing="back"
                      onBarcodeScanned={scanned ? undefined : handleBarCodeScanned}
                      barcodeScannerSettings={{
                        barcodeTypes: ['qr'],
                      }}
                    />
                    <View style={styles.scanOverlay}>
                      <View style={styles.scanFrame} />
                      <Text style={styles.scanHint}>Aponte para o QR Code do cliente</Text>
                    </View>
                    {isValidating && (
                      <View style={styles.scanningOverlay}>
                        <ActivityIndicator size="large" color="#10B981" />
                        <Text style={styles.scanningText}>Validando...</Text>
                      </View>
                    )}
                  </View>
                )}
              </View>
            ) : (
              // Manual Input
              <View style={styles.manualContainer}>
                <View style={styles.inputIcon}>
                  <Ionicons name="keypad" size={48} color="#3B82F6" />
                </View>
                <Text style={styles.inputTitle}>Digite o Código</Text>
                <Text style={styles.inputHint}>
                  Digite o código de 16 caracteres ou o código de backup (ITK-XXX)
                </Text>
                <TextInput
                  style={styles.input}
                  value={codeInput}
                  onChangeText={setCodeInput}
                  placeholder="Ex: ITK-ABC ou código QR"
                  placeholderTextColor="#64748B"
                  autoCapitalize="characters"
                  autoCorrect={false}
                />
                <TouchableOpacity
                  style={[styles.validateButton, !codeInput.trim() && styles.validateButtonDisabled]}
                  onPress={() => handleValidate(codeInput)}
                  disabled={isValidating || !codeInput.trim()}
                >
                  {isValidating ? (
                    <ActivityIndicator color="#FFFFFF" />
                  ) : (
                    <>
                      <Ionicons name="checkmark-circle" size={20} color="#FFFFFF" />
                      <Text style={styles.validateButtonText}>Validar Código</Text>
                    </>
                  )}
                </TouchableOpacity>
              </View>
            )}
          </>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0F172A' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1E293B',
  },
  backButton: { marginRight: 16 },
  title: { fontSize: 20, fontWeight: '700', color: '#FFFFFF' },
  content: { flex: 1 },
  contentContainer: { padding: 20 },
  
  // Mode Selector
  modeSelector: {
    flexDirection: 'row',
    backgroundColor: '#1E293B',
    borderRadius: 12,
    padding: 4,
    marginBottom: 20,
  },
  modeButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 10,
    gap: 8,
  },
  modeButtonActive: { backgroundColor: '#3B82F6' },
  modeButtonText: { fontSize: 15, fontWeight: '600', color: '#64748B' },
  modeButtonTextActive: { color: '#FFFFFF' },
  
  // Scanner
  scannerContainer: { flex: 1, minHeight: 400 },
  permissionContainer: { alignItems: 'center', justifyContent: 'center', padding: 40 },
  permissionTitle: { fontSize: 18, fontWeight: '700', color: '#FFFFFF', marginTop: 16 },
  permissionText: { fontSize: 14, color: '#94A3B8', textAlign: 'center', marginTop: 8 },
  manualButton: { backgroundColor: '#3B82F6', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 10, marginTop: 20 },
  manualButtonText: { fontSize: 16, fontWeight: '600', color: '#FFFFFF' },
  cameraContainer: { borderRadius: 16, overflow: 'hidden', height: 350 },
  camera: { flex: 1 },
  scanOverlay: { ...StyleSheet.absoluteFillObject, alignItems: 'center', justifyContent: 'center' },
  scanFrame: { width: 250, height: 250, borderWidth: 3, borderColor: '#10B981', borderRadius: 16 },
  scanHint: { fontSize: 14, color: '#FFFFFF', marginTop: 20, backgroundColor: 'rgba(0,0,0,0.6)', paddingHorizontal: 16, paddingVertical: 8, borderRadius: 8 },
  scanningOverlay: { ...StyleSheet.absoluteFillObject, backgroundColor: 'rgba(0,0,0,0.7)', alignItems: 'center', justifyContent: 'center' },
  scanningText: { fontSize: 16, color: '#FFFFFF', marginTop: 16 },
  
  // Manual Input
  manualContainer: { alignItems: 'center', paddingVertical: 20 },
  inputIcon: { width: 80, height: 80, borderRadius: 40, backgroundColor: '#1E293B', justifyContent: 'center', alignItems: 'center', marginBottom: 20 },
  inputTitle: { fontSize: 20, fontWeight: '700', color: '#FFFFFF', marginBottom: 8 },
  inputHint: { fontSize: 14, color: '#94A3B8', textAlign: 'center', marginBottom: 20, paddingHorizontal: 20 },
  input: { backgroundColor: '#1E293B', borderRadius: 12, paddingHorizontal: 20, paddingVertical: 16, fontSize: 18, color: '#FFFFFF', width: '100%', textAlign: 'center', borderWidth: 1, borderColor: '#334155', letterSpacing: 2 },
  validateButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#10B981', paddingVertical: 16, borderRadius: 12, width: '100%', marginTop: 20, gap: 8 },
  validateButtonDisabled: { opacity: 0.5 },
  validateButtonText: { fontSize: 18, fontWeight: '700', color: '#FFFFFF' },
  
  // Result
  resultContainer: { alignItems: 'center' },
  successIcon: { marginBottom: 16 },
  successTitle: { fontSize: 24, fontWeight: '800', color: '#10B981', marginBottom: 24, textAlign: 'center' },
  
  saleCard: { backgroundColor: '#1E293B', borderRadius: 16, padding: 20, width: '100%', borderWidth: 1, borderColor: '#334155' },
  saleHeader: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 16 },
  saleHeaderTitle: { fontSize: 18, fontWeight: '700', color: '#FFFFFF' },
  saleRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  saleLabel: { fontSize: 14, color: '#94A3B8' },
  saleValue: { fontSize: 14, fontWeight: '600', color: '#FFFFFF' },
  saleValueCode: { fontSize: 16, fontWeight: '800', color: '#F59E0B', letterSpacing: 2 },
  divider: { height: 1, backgroundColor: '#334155', marginVertical: 16 },
  
  creditsRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1E3A5F', padding: 12, borderRadius: 10, marginTop: 8 },
  creditsIcon: { marginRight: 12 },
  creditsInfo: { flex: 1 },
  creditsLabel: { fontSize: 12, color: '#93C5FD' },
  creditsValue: { fontSize: 18, fontWeight: '700', color: '#3B82F6' },
  
  cashRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#064E3B', padding: 16, borderRadius: 12, marginTop: 12 },
  cashIcon: { marginRight: 12 },
  cashInfo: { flex: 1 },
  cashLabel: { fontSize: 12, color: '#A7F3D0', fontWeight: '600' },
  cashValue: { fontSize: 28, fontWeight: '800', color: '#10B981' },
  
  creditAddedInfo: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#064E3B', padding: 12, borderRadius: 10, marginTop: 16, gap: 8, width: '100%' },
  creditAddedText: { fontSize: 13, color: '#A7F3D0', flex: 1 },
  
  newScanButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#3B82F6', paddingVertical: 16, borderRadius: 12, width: '100%', marginTop: 24, gap: 8 },
  newScanButtonText: { fontSize: 16, fontWeight: '700', color: '#FFFFFF' },
});
