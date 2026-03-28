import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TouchableOpacity,
  ActivityIndicator,
  Share,
  Platform,
  TextInput,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import QRCode from 'react-native-qrcode-svg';
import { Offer, QRCode as QRCodeType } from '../types';

interface QRModalProps {
  visible: boolean;
  onClose: () => void;
  offer: Offer | null;
  qrCode: QRCodeType | null;
  isGenerating: boolean;
  onGenerate: (useCredits?: number) => void;
  userTokens: number;
  userCredits?: number;
}

export const QRModal: React.FC<QRModalProps> = ({
  visible,
  onClose,
  offer,
  qrCode,
  isGenerating,
  onGenerate,
  userTokens,
  userCredits = 0,
}) => {
  const router = useRouter();
  const [paymentMethod, setPaymentMethod] = useState<'token' | 'credits'>('token');
  const [creditsToUse, setCreditsToUse] = useState('1');

  const formatPrice = (price: number) => {
    return `R$ ${price.toFixed(2).replace('.', ',')}`;
  };

  const handleShare = async () => {
    if (qrCode) {
      try {
        await Share.share({
          message: `Use o código ${qrCode.code_hash} para resgatar ${offer?.title} com ${offer?.discount_value}% de desconto!`,
        });
      } catch (error) {
        console.error('Share error:', error);
      }
    }
  };

  const getExpiresIn = () => {
    if (!qrCode) return '';
    const expires = new Date(qrCode.expires_at);
    const now = new Date();
    const days = Math.floor((expires.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    if (days > 30) {
      const months = Math.floor(days / 30);
      return `Válido por ${months} ${months === 1 ? 'mês' : 'meses'}`;
    }
    return `Válido por ${days} dias`;
  };

  const handleBuyTokens = () => {
    onClose();
    setTimeout(() => {
      router.push('/buy-tokens');
    }, 300);
  };

  const handleGenerate = () => {
    if (paymentMethod === 'credits') {
      const credits = parseFloat(creditsToUse) || 1;
      onGenerate(credits);
    } else {
      onGenerate(0);
    }
  };

  const canGenerateWithTokens = userTokens >= 1;
  const canGenerateWithCredits = userCredits >= 1;
  const canGenerate = canGenerateWithTokens || canGenerateWithCredits;

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={true}
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <View style={styles.container}>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Ionicons name="close" size={24} color="#94A3B8" />
          </TouchableOpacity>

          {offer && (
            <>
              <Text style={styles.title}>{offer.title}</Text>
              <View style={styles.priceRow}>
                <Text style={styles.discount}>{offer.discount_value}% OFF</Text>
                <Text style={styles.price}>{formatPrice(offer.discounted_price)}</Text>
              </View>

              {qrCode ? (
                <View style={styles.qrContainer}>
                  <View style={styles.qrWrapper}>
                    <QRCode
                      value={qrCode.code_hash}
                      size={200}
                      backgroundColor="#FFFFFF"
                      color="#0F172A"
                    />
                  </View>
                  <Text style={styles.codeText}>{qrCode.code_hash}</Text>
                  {qrCode.offer_code && (
                    <Text style={styles.offerCodeText}>Código: {qrCode.offer_code}</Text>
                  )}
                  <Text style={styles.expiresText}>{getExpiresIn()}</Text>

                  <TouchableOpacity style={styles.shareButton} onPress={handleShare}>
                    <Ionicons name="share-outline" size={20} color="#0F172A" />
                    <Text style={styles.shareButtonText}>Compartilhar</Text>
                  </TouchableOpacity>

                  <Text style={styles.instructionText}>
                    Apresente este QR Code no estabelecimento para resgatar seu desconto
                  </Text>
                </View>
              ) : (
                <View style={styles.generateContainer}>
                  {canGenerate ? (
                    <>
                      {/* Balance Summary */}
                      <View style={styles.balanceSummary}>
                        <View style={styles.balanceItem}>
                          <Ionicons name="ticket" size={20} color="#10B981" />
                          <Text style={styles.balanceLabel}>Tokens:</Text>
                          <Text style={[styles.balanceValue, !canGenerateWithTokens && styles.balanceZero]}>
                            {userTokens}
                          </Text>
                        </View>
                        <View style={styles.balanceDivider} />
                        <View style={styles.balanceItem}>
                          <Ionicons name="wallet" size={20} color="#3B82F6" />
                          <Text style={styles.balanceLabel}>Créditos:</Text>
                          <Text style={[styles.balanceValue, styles.creditValue, !canGenerateWithCredits && styles.balanceZero]}>
                            R$ {userCredits.toFixed(2).replace('.', ',')}
                          </Text>
                        </View>
                      </View>

                      {/* Payment Method Selection */}
                      <Text style={styles.sectionTitle}>Escolha como pagar:</Text>
                      
                      <View style={styles.paymentOptions}>
                        {/* Token Option */}
                        <TouchableOpacity
                          style={[
                            styles.paymentOption,
                            paymentMethod === 'token' && styles.paymentOptionSelected,
                            !canGenerateWithTokens && styles.paymentOptionDisabled
                          ]}
                          onPress={() => canGenerateWithTokens && setPaymentMethod('token')}
                          disabled={!canGenerateWithTokens}
                        >
                          <View style={styles.paymentOptionHeader}>
                            <Ionicons 
                              name={paymentMethod === 'token' ? 'radio-button-on' : 'radio-button-off'} 
                              size={20} 
                              color={paymentMethod === 'token' ? '#10B981' : '#64748B'} 
                            />
                            <Ionicons name="ticket" size={20} color="#10B981" />
                            <Text style={styles.paymentOptionTitle}>1 Token</Text>
                          </View>
                          {!canGenerateWithTokens && (
                            <Text style={styles.insufficientText}>Saldo insuficiente</Text>
                          )}
                        </TouchableOpacity>

                        {/* Credits Option */}
                        <TouchableOpacity
                          style={[
                            styles.paymentOption,
                            paymentMethod === 'credits' && styles.paymentOptionSelected,
                            !canGenerateWithCredits && styles.paymentOptionDisabled
                          ]}
                          onPress={() => canGenerateWithCredits && setPaymentMethod('credits')}
                          disabled={!canGenerateWithCredits}
                        >
                          <View style={styles.paymentOptionHeader}>
                            <Ionicons 
                              name={paymentMethod === 'credits' ? 'radio-button-on' : 'radio-button-off'} 
                              size={20} 
                              color={paymentMethod === 'credits' ? '#3B82F6' : '#64748B'} 
                            />
                            <Ionicons name="wallet" size={20} color="#3B82F6" />
                            <Text style={styles.paymentOptionTitle}>Usar Créditos</Text>
                          </View>
                          {canGenerateWithCredits && paymentMethod === 'credits' && (
                            <View style={styles.creditsInputRow}>
                              <Text style={styles.creditsInputLabel}>R$</Text>
                              <TextInput
                                style={styles.creditsInput}
                                value={creditsToUse}
                                onChangeText={setCreditsToUse}
                                keyboardType="decimal-pad"
                                placeholder="1.00"
                                placeholderTextColor="#64748B"
                              />
                              <Text style={styles.creditsMax}>(máx: {userCredits.toFixed(2)})</Text>
                            </View>
                          )}
                          {!canGenerateWithCredits && (
                            <Text style={styles.insufficientText}>Sem créditos disponíveis</Text>
                          )}
                        </TouchableOpacity>
                      </View>

                      <TouchableOpacity
                        style={styles.generateButton}
                        onPress={handleGenerate}
                        disabled={isGenerating}
                      >
                        {isGenerating ? (
                          <ActivityIndicator color="#0F172A" />
                        ) : (
                          <>
                            <Ionicons name="qr-code" size={20} color="#0F172A" />
                            <Text style={styles.generateButtonText}>Gerar QR Code</Text>
                          </>
                        )}
                      </TouchableOpacity>
                    </>
                  ) : (
                    <>
                      {/* Zero balance state */}
                      <View style={styles.noTokensIcon}>
                        <Ionicons name="wallet-outline" size={48} color="#EF4444" />
                      </View>
                      <Text style={styles.noTokensTitle}>Saldo Insuficiente</Text>
                      <Text style={styles.noTokensText}>
                        Você não possui tokens ou créditos suficientes. Compre um pacote de tokens ou ganhe créditos indicando amigos!
                      </Text>

                      <View style={styles.balanceSummary}>
                        <View style={styles.balanceItem}>
                          <Ionicons name="ticket" size={20} color="#EF4444" />
                          <Text style={styles.balanceLabel}>Tokens:</Text>
                          <Text style={[styles.balanceValue, styles.balanceZero]}>{userTokens}</Text>
                        </View>
                        <View style={styles.balanceDivider} />
                        <View style={styles.balanceItem}>
                          <Ionicons name="wallet" size={20} color="#EF4444" />
                          <Text style={styles.balanceLabel}>Créditos:</Text>
                          <Text style={[styles.balanceValue, styles.balanceZero]}>
                            R$ {userCredits.toFixed(2).replace('.', ',')}
                          </Text>
                        </View>
                      </View>

                      <TouchableOpacity
                        style={styles.buyTokensButton}
                        onPress={handleBuyTokens}
                      >
                        <Ionicons name="cart" size={20} color="#0F172A" />
                        <Text style={styles.buyTokensText}>
                          Comprar Pacote de Tokens (R$ 7,00)
                        </Text>
                      </TouchableOpacity>
                    </>
                  )}
                </View>
              )}
            </>
          )}
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'flex-end',
  },
  container: {
    backgroundColor: '#1E293B',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    paddingBottom: 40,
    maxHeight: '90%',
  },
  closeButton: {
    position: 'absolute',
    top: 16,
    right: 16,
    zIndex: 1,
    padding: 4,
  },
  title: {
    fontSize: 20,
    fontWeight: '700',
    color: '#FFFFFF',
    marginBottom: 8,
    paddingRight: 40,
  },
  priceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    gap: 12,
  },
  discount: {
    backgroundColor: '#10B981',
    color: '#0F172A',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    fontSize: 14,
    fontWeight: '600',
    overflow: 'hidden',
  },
  price: {
    fontSize: 24,
    fontWeight: '700',
    color: '#10B981',
  },
  qrContainer: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  qrWrapper: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 16,
  },
  codeText: {
    marginTop: 16,
    fontSize: 18,
    fontWeight: '600',
    color: '#FFFFFF',
    letterSpacing: 2,
  },
  offerCodeText: {
    marginTop: 8,
    fontSize: 14,
    fontWeight: '600',
    color: '#3B82F6',
    backgroundColor: '#1E3A5F',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 8,
  },
  expiresText: {
    marginTop: 8,
    fontSize: 14,
    color: '#10B981',
  },
  shareButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#10B981',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
    marginTop: 20,
    gap: 8,
  },
  shareButtonText: {
    color: '#0F172A',
    fontSize: 16,
    fontWeight: '600',
  },
  instructionText: {
    marginTop: 20,
    fontSize: 14,
    color: '#94A3B8',
    textAlign: 'center',
    lineHeight: 20,
  },
  generateContainer: {
    alignItems: 'center',
    paddingVertical: 10,
  },
  balanceSummary: {
    flexDirection: 'row',
    backgroundColor: '#0F172A',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
    width: '100%',
  },
  balanceItem: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
  },
  balanceDivider: {
    width: 1,
    backgroundColor: '#334155',
    marginHorizontal: 12,
  },
  balanceLabel: {
    fontSize: 13,
    color: '#94A3B8',
  },
  balanceValue: {
    fontSize: 16,
    fontWeight: '700',
    color: '#10B981',
  },
  creditValue: {
    color: '#3B82F6',
  },
  balanceZero: {
    color: '#EF4444',
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#FFFFFF',
    marginBottom: 12,
    alignSelf: 'flex-start',
  },
  paymentOptions: {
    width: '100%',
    gap: 10,
    marginBottom: 20,
  },
  paymentOption: {
    backgroundColor: '#0F172A',
    borderRadius: 12,
    padding: 14,
    borderWidth: 2,
    borderColor: '#334155',
  },
  paymentOptionSelected: {
    borderColor: '#10B981',
  },
  paymentOptionDisabled: {
    opacity: 0.5,
  },
  paymentOptionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  paymentOptionTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  insufficientText: {
    fontSize: 12,
    color: '#EF4444',
    marginTop: 6,
    marginLeft: 30,
  },
  creditsInputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
    marginLeft: 30,
    gap: 8,
  },
  creditsInputLabel: {
    fontSize: 14,
    color: '#94A3B8',
  },
  creditsInput: {
    backgroundColor: '#1E293B',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 16,
    color: '#FFFFFF',
    width: 80,
    textAlign: 'center',
  },
  creditsMax: {
    fontSize: 12,
    color: '#64748B',
  },
  generateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#10B981',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
    gap: 8,
    width: '100%',
    justifyContent: 'center',
  },
  generateButtonText: {
    color: '#0F172A',
    fontSize: 18,
    fontWeight: '600',
  },
  noTokensIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#EF444420',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  noTokensTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#EF4444',
    marginBottom: 12,
  },
  noTokensText: {
    fontSize: 14,
    color: '#94A3B8',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 16,
    paddingHorizontal: 8,
  },
  buyTokensButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#10B981',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderRadius: 14,
    gap: 8,
    width: '100%',
  },
  buyTokensText: {
    color: '#0F172A',
    fontSize: 16,
    fontWeight: '700',
  },
});
