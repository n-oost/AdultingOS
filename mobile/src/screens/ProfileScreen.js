/**
 * Profile Screen - User settings and app information
 */
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';

const ProfileScreen = () => {
  const handleSettingPress = (setting) => {
    // TODO: Implement settings navigation
    console.log(`Pressed: ${setting}`);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>AdultingOS</Text>
        <Text style={styles.subtitle}>Your Life Admin Assistant</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Settings</Text>
        
        <TouchableOpacity 
          style={styles.settingItem}
          onPress={() => handleSettingPress('notifications')}
        >
          <Text style={styles.settingText}>Notifications</Text>
          <Text style={styles.settingArrow}>›</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.settingItem}
          onPress={() => handleSettingPress('backup')}
        >
          <Text style={styles.settingText}>Backup & Sync</Text>
          <Text style={styles.settingArrow}>›</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.settingItem}
          onPress={() => handleSettingPress('privacy')}
        >
          <Text style={styles.settingText}>Privacy</Text>
          <Text style={styles.settingArrow}>›</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        
        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>Version</Text>
          <Text style={styles.infoValue}>1.0.0</Text>
        </View>

        <TouchableOpacity 
          style={styles.settingItem}
          onPress={() => handleSettingPress('help')}
        >
          <Text style={styles.settingText}>Help & Support</Text>
          <Text style={styles.settingArrow}>›</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.settingItem}
          onPress={() => handleSettingPress('privacy-policy')}
        >
          <Text style={styles.settingText}>Privacy Policy</Text>
          <Text style={styles.settingArrow}>›</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: 24,
    alignItems: 'center',
    backgroundColor: '#fff',
    marginBottom: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginTop: 4,
  },
  section: {
    backgroundColor: '#fff',
    marginBottom: 16,
    paddingVertical: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e293b',
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  settingText: {
    fontSize: 16,
    color: '#1e293b',
  },
  settingArrow: {
    fontSize: 20,
    color: '#6b7280',
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  infoLabel: {
    fontSize: 16,
    color: '#1e293b',
  },
  infoValue: {
    fontSize: 16,
    color: '#6b7280',
  },
});

export default ProfileScreen;