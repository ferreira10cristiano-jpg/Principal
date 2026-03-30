import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Platform,
  Image,
  Linking,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../src/store/authStore';
import { api } from '../../src/lib/api';
import { Transaction, NetworkData } from '../../src/types';
import { ShareInviteModal } from '../../src/components/ShareInviteModal';

export default function WalletScreen() {
  const insets = useSafeAreaInsets();
  const router = useRouter();
  const { user, refreshUser } = useAuthStore();
  const [credits, setCredits] = useState<{ balance: number; transactions: Transaction[] } | null>(null);
  const [networkData, setNetworkData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [shareModalVisible, setShareModalVisible] = useState(false);
  const [shareType, setShareType] = useState<'friend' | 'establishment'>('friend');
  const [mediaAssets, setMediaAssets] = useState<any[]>([]);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [creditsData, network, media] = await Promise.all([
        api.getMyCredits(),
        api.getMyNetwork(),
        api.getPublicMedia().catch(() => []),
      ]);
      setCredits(creditsData);
      setNetworkData(network);
      setMediaAssets(media);
      await refreshUser();
    } catch (error) {
      console.error('Error loading wallet data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  }, []);

  const handleCopyCode = () => {
    if (networkData?.referral_code) {
      if (Platform.OS === 'web') {
        navigator.clipboard?.writeText(networkData.referral_code);
        window.alert('Codigo copiado!');
      } else {
        try { require('react-native').Clipboard.setString(networkData.referral_code); } catch (e) {}
      }
    }
  };

  const handleDownloadMedia = (url: string) => {
    if (Platform.OS === 'web') {
      window.open(url, '_blank');
    } else {
      Linking.openURL(url);
    }
  };

  if (isLoading) {
    return (
      <View style={[s.root, s.centered, { paddingTop: insets.top }]}>
        <ActivityIndicator size="large" color="#10B981" />
      </View>
    );
  }

  const balance = credits?.balance || 0;
  const transactions = credits?.transactions || [];
  const tokens = user?.tokens || 0;
  const stats = networkData?.network_stats || {};
  const l1 = stats.level1 || { total: 0, active: 0, credits: 0 };
  const l2 = stats.level2 || { total: 0, active: 0, credits: 0 };
  const l3 = stats.level3 || { total: 0, active: 0, credits: 0 };
  const est = stats.establishments || { total: 0, active: 0, credits: 0 };
  const totalSavings = transactions.reduce((sum: number, t: Transaction) => sum + Math.max(0, t.amount || 0), 0);
  const fmtPrice = (v: number) => `R$ ${v.toFixed(2).replace('.', ',')}`;

  return (
    <View style={[s.root, { paddingTop: insets.top }]}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={s.scrollContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#10B981" colors={['#10B981']} />}
      >
        {/* ===== HERO ===== */}
        <View style={s.hero} data-testid="wallet-hero">
          <Text style={s.heroTitle}>Creditos</Text>
          <View style={s.heroBalanceRow}>
            <Text style={s.heroCurrency}>R$</Text>
            <Text style={s.heroBalance}>{balance.toFixed(2)}</Text>
          </View>
          <Text style={s.heroImpact}>Seus creditos podem ser usados para pagar suas compras!</Text>
          <View style={s.heroMeta}>
            <View style={s.heroSavingsPill}>
              <Ionicons name="trending-up" size={13} color="#6EE7B7" />
              <Text style={s.heroSavingsText}>Economia total: {fmtPrice(totalSavings)}</Text>
            </View>
            <TouchableOpacity
              style={s.helpBtn}
              onPress={() => router.push('/(tabs)/help')}
              activeOpacity={0.7}
              data-testid="how-to-earn-btn"
            >
              <Ionicons name="help-circle-outline" size={15} color="#10B981" />
              <Text style={s.helpBtnText}>Como ganhar creditos</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* ===== TOKENS ===== */}
        <View style={s.section}>
          <View style={s.tokenCard} data-testid="wallet-tokens">
            <View style={s.tokenLeft}>
              <View style={s.tokenIcon}>
                <Ionicons name="ticket" size={18} color="#10B981" />
              </View>
              <View>
                <Text style={s.tokenTitle}>Meus Tokens</Text>
                <Text style={s.tokenSub}>Para gerar QR Codes</Text>
              </View>
            </View>
            <Text style={s.tokenCount}>{tokens}</Text>
            <TouchableOpacity
              style={s.tokenBuyBtn}
              onPress={() => router.push('/buy-tokens')}
              activeOpacity={0.7}
              data-testid="buy-tokens-btn"
            >
              <Ionicons name="add" size={16} color="#10B981" />
              <Text style={s.tokenBuyText}>Comprar</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* ===== GANHE CREDITOS INDICANDO ===== */}
        <View style={s.section}>
          <Text style={s.sectionTitle}>Ganhe creditos indicando</Text>
          <View style={s.referralCard} data-testid="wallet-referral">
            <View style={s.referralBtns}>
              <TouchableOpacity
                style={s.referralBtn}
                onPress={() => { setShareType('friend'); setShareModalVisible(true); }}
                activeOpacity={0.7}
                data-testid="share-friend-btn"
              >
                <View style={s.referralBtnIcon}>
                  <Ionicons name="person-add-outline" size={18} color="#10B981" />
                </View>
                <Text style={s.referralBtnLabel}>Indicar Amigo</Text>
              </TouchableOpacity>
              <View style={s.referralDivider} />
              <TouchableOpacity
                style={s.referralBtn}
                onPress={() => { setShareType('establishment'); setShareModalVisible(true); }}
                activeOpacity={0.7}
                data-testid="share-store-btn"
              >
                <View style={s.referralBtnIcon}>
                  <Ionicons name="storefront-outline" size={18} color="#10B981" />
                </View>
                <Text style={s.referralBtnLabel}>Indicar Loja</Text>
              </TouchableOpacity>
            </View>
            <TouchableOpacity style={s.codeRow} onPress={handleCopyCode} activeOpacity={0.6}>
              <Ionicons name="link-outline" size={14} color="#475569" />
              <Text style={s.codeText}>{networkData?.referral_code || '---'}</Text>
              <Ionicons name="copy-outline" size={14} color="#475569" />
            </TouchableOpacity>
          </View>
        </View>

        {/* ===== BANCO DE MIDIA ===== */}
        {mediaAssets.length > 0 && (
          <View style={s.section}>
            <Text style={s.sectionTitle}>Materiais para divulgar</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={s.mediaScroll}>
              {mediaAssets.map((asset) => (
                <TouchableOpacity
                  key={asset.media_id}
                  style={s.mediaCard}
                  onPress={() => handleDownloadMedia(asset.url)}
                  activeOpacity={0.7}
                  data-testid={`media-${asset.media_id}`}
                >
                  {asset.type === 'image' ? (
                    <Image source={{ uri: asset.url }} style={s.mediaThumb} resizeMode="cover" />
                  ) : (
                    <View style={s.mediaVideoThumb}>
                      <Ionicons name="play-circle" size={32} color="#10B981" />
                    </View>
                  )}
                  <Text style={s.mediaTitle} numberOfLines={1}>{asset.title}</Text>
                  <View style={s.mediaDownload}>
                    <Ionicons name="download-outline" size={14} color="#10B981" />
                    <Text style={s.mediaDownloadText}>Baixar</Text>
                  </View>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}

        {/* ===== MINHA REDE ===== */}
        <View style={s.section}>
          <Text style={s.sectionTitle}>Minha Rede</Text>
          <View style={s.netCard} data-testid="wallet-network">
            {/* Header */}
            <View style={s.netHeader}>
              <Text style={[s.netHeaderCell, { flex: 2 }]}></Text>
              <Text style={s.netHeaderCell}>Indicados</Text>
              <Text style={s.netHeaderCell}>Ativos</Text>
              <Text style={s.netHeaderCell}>Creditos</Text>
            </View>
            {/* Level rows */}
            <NetRow label="Nivel 1" sub="Diretos" color="#10B981" total={l1.total} active={l1.active} credits={l1.credits} />
            <View style={s.netSep} />
            <NetRow label="Nivel 2" sub="" color="#3B82F6" total={l2.total} active={l2.active} credits={l2.credits} />
            <View style={s.netSep} />
            <NetRow label="Nivel 3" sub="" color="#F59E0B" total={l3.total} active={l3.active} credits={l3.credits} />
            <View style={s.netSep} />
            <NetRow label="Estabelecimentos" sub="" color="#8B5CF6" total={est.total} active={est.active} credits={est.credits} />
          </View>
        </View>

        {/* ===== HISTORICO ===== */}
        {transactions.length > 0 && (
          <View style={s.section}>
            <Text style={s.sectionTitle}>Historico</Text>
            <View style={s.txList}>
              {transactions.slice(0, 8).map((item: Transaction, index: number) => (
                <View key={index} style={s.txRow}>
                  <View style={[s.txDot, item.amount < 0 && { backgroundColor: '#EF4444' }]} />
                  <View style={s.txBody}>
                    <Text style={s.txDesc} numberOfLines={1}>{item.description}</Text>
                    <Text style={s.txDate}>
                      {new Date(item.created_at).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })}
                    </Text>
                  </View>
                  <Text style={[s.txAmt, item.amount < 0 && { color: '#EF4444' }]}>
                    {item.amount >= 0 ? '+' : ''}R$ {item.amount.toFixed(2)}
                  </Text>
                </View>
              ))}
            </View>
          </View>
        )}

        <View style={{ height: 40 }} />
      </ScrollView>

      <ShareInviteModal
        visible={shareModalVisible}
        onClose={() => setShareModalVisible(false)}
        referralCode={networkData?.referral_code || ''}
        userName={user?.name || ''}
        type={shareType}
      />
    </View>
  );
}

function NetRow({ label, sub, color, total, active, credits }: {
  label: string; sub: string; color: string; total: number; active: number; credits: number;
}) {
  return (
    <View style={s.netRow}>
      <View style={[s.netCell, { flex: 2, flexDirection: 'row', alignItems: 'center', gap: 8 }]}>
        <View style={[s.netDot, { backgroundColor: color }]} />
        <View>
          <Text style={s.netLabel}>{label}</Text>
          {sub ? <Text style={s.netSub}>{sub}</Text> : null}
        </View>
      </View>
      <Text style={s.netValue}>{total}</Text>
      <Text style={[s.netValue, { color: active > 0 ? '#10B981' : '#475569' }]}>{active}</Text>
      <Text style={[s.netValue, { color: credits > 0 ? '#10B981' : '#475569' }]}>
        {credits > 0 ? `R$${credits.toFixed(0)}` : '—'}
      </Text>
    </View>
  );
}

const s = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#0B0F1A' },
  centered: { justifyContent: 'center', alignItems: 'center' },
  scrollContent: { paddingBottom: 20 },

  /* HERO */
  hero: { paddingHorizontal: 24, paddingTop: 20, paddingBottom: 24 },
  heroTitle: {
    fontSize: 28,
    fontWeight: '800',
    color: '#E2E8F0',
    letterSpacing: -0.5,
  },
  heroBalanceRow: { flexDirection: 'row', alignItems: 'baseline', marginTop: 8 },
  heroCurrency: { fontSize: 20, fontWeight: '600', color: '#10B981', marginRight: 4 },
  heroBalance: { fontSize: 46, fontWeight: '800', color: '#10B981', letterSpacing: -1.5 },
  heroImpact: {
    fontSize: 14,
    fontWeight: '600',
    color: '#94A3B8',
    marginTop: 8,
    lineHeight: 20,
  },
  heroMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 14,
    gap: 10,
    flexWrap: 'wrap',
  },
  heroSavingsPill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    backgroundColor: '#10B98110',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 20,
  },
  heroSavingsText: { fontSize: 12, fontWeight: '600', color: '#6EE7B7' },
  helpBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    borderWidth: 1,
    borderColor: '#10B98130',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 20,
  },
  helpBtnText: { fontSize: 12, fontWeight: '600', color: '#10B981' },

  /* SECTIONS */
  section: { marginTop: 28, paddingHorizontal: 24 },
  sectionTitle: { fontSize: 15, fontWeight: '700', color: '#CBD5E1', marginBottom: 14 },

  /* TOKENS */
  tokenCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#111827',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#1E293B',
  },
  tokenLeft: { flexDirection: 'row', alignItems: 'center', gap: 12, flex: 1 },
  tokenIcon: {
    width: 38, height: 38, borderRadius: 10,
    backgroundColor: '#10B98115', justifyContent: 'center', alignItems: 'center',
  },
  tokenTitle: { fontSize: 14, fontWeight: '600', color: '#E2E8F0' },
  tokenSub: { fontSize: 11, color: '#475569', marginTop: 1 },
  tokenCount: { fontSize: 26, fontWeight: '800', color: '#E2E8F0', marginRight: 14 },
  tokenBuyBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    borderWidth: 1, borderColor: '#10B98140', borderRadius: 10,
    paddingHorizontal: 12, paddingVertical: 8,
  },
  tokenBuyText: { fontSize: 13, fontWeight: '600', color: '#10B981' },

  /* REFERRAL */
  referralCard: {
    backgroundColor: '#111827', borderRadius: 16,
    borderWidth: 1, borderColor: '#1E293B', overflow: 'hidden',
  },
  referralBtns: { flexDirection: 'row', alignItems: 'center' },
  referralBtn: { flex: 1, alignItems: 'center', paddingVertical: 18, gap: 8 },
  referralBtnIcon: {
    width: 40, height: 40, borderRadius: 20,
    backgroundColor: '#10B98112', justifyContent: 'center', alignItems: 'center',
  },
  referralBtnLabel: { fontSize: 13, fontWeight: '600', color: '#CBD5E1' },
  referralDivider: { width: 1, height: 40, backgroundColor: '#1E293B' },
  codeRow: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: 8, paddingVertical: 12,
    borderTopWidth: 1, borderTopColor: '#1E293B', backgroundColor: '#0D111D',
  },
  codeText: { fontSize: 13, fontWeight: '700', color: '#475569', letterSpacing: 1.5 },

  /* MEDIA */
  mediaScroll: { marginHorizontal: -4 },
  mediaCard: {
    width: 140, backgroundColor: '#111827', borderRadius: 14,
    borderWidth: 1, borderColor: '#1E293B', marginHorizontal: 4, overflow: 'hidden',
  },
  mediaThumb: { width: '100%', height: 100 },
  mediaVideoThumb: {
    width: '100%', height: 100,
    backgroundColor: '#0D111D', justifyContent: 'center', alignItems: 'center',
  },
  mediaTitle: { fontSize: 12, fontWeight: '600', color: '#CBD5E1', paddingHorizontal: 10, paddingTop: 8 },
  mediaDownload: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    paddingHorizontal: 10, paddingVertical: 8,
  },
  mediaDownloadText: { fontSize: 11, fontWeight: '600', color: '#10B981' },

  /* NETWORK TABLE */
  netCard: {
    backgroundColor: '#111827', borderRadius: 16,
    borderWidth: 1, borderColor: '#1E293B', overflow: 'hidden',
  },
  netHeader: {
    flexDirection: 'row', paddingHorizontal: 16, paddingVertical: 10,
    backgroundColor: '#0D111D', borderBottomWidth: 1, borderBottomColor: '#1E293B',
  },
  netHeaderCell: {
    flex: 1, fontSize: 11, fontWeight: '700', color: '#475569',
    textTransform: 'uppercase', letterSpacing: 0.5, textAlign: 'center',
  },
  netRow: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 14 },
  netCell: { flex: 1 },
  netDot: { width: 8, height: 8, borderRadius: 4 },
  netLabel: { fontSize: 13, fontWeight: '600', color: '#CBD5E1' },
  netSub: { fontSize: 10, color: '#475569', marginTop: 1 },
  netValue: {
    flex: 1, fontSize: 14, fontWeight: '700', color: '#CBD5E1', textAlign: 'center',
  },
  netSep: { height: 1, backgroundColor: '#1E293B', marginHorizontal: 16 },

  /* TRANSACTIONS */
  txList: {
    backgroundColor: '#111827', borderRadius: 16,
    borderWidth: 1, borderColor: '#1E293B', paddingVertical: 4,
  },
  txRow: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 18, paddingVertical: 12,
    borderBottomWidth: 1, borderBottomColor: '#1E293B',
  },
  txDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#10B981', marginRight: 12 },
  txBody: { flex: 1 },
  txDesc: { fontSize: 13, fontWeight: '500', color: '#CBD5E1' },
  txDate: { fontSize: 11, color: '#475569', marginTop: 2 },
  txAmt: { fontSize: 14, fontWeight: '700', color: '#10B981' },
});
