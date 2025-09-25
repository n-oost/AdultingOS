/**
 * Tasks Screen - Display and manage user tasks
 */
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  Alert,
} from 'react-native';
import { apiService } from '../services/apiService';

const TasksScreen = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadTasks = async () => {
    setLoading(true);
    try {
      const response = await apiService.chat('/task list');
      // Parse task list from assistant response
      setTasks(parseTasks(response.reply));
    } catch (error) {
      Alert.alert('Error', 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const parseTasks = (taskText) => {
    // Simple parser for task list format
    const lines = taskText.split('\n').filter(line => line.trim());
    return lines.map((line, index) => {
      const isCompleted = line.startsWith('✔');
      const title = line.replace(/^[•✔]\s*/, '').split('[')[0].trim();
      return {
        id: index.toString(),
        title,
        completed: isCompleted,
      };
    });
  };

  const toggleTask = async (taskId) => {
    try {
      await apiService.chat(`/task done ${taskId}`);
      loadTasks(); // Refresh list
    } catch (error) {
      Alert.alert('Error', 'Failed to update task');
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const renderTask = ({ item }) => (
    <TouchableOpacity
      style={[styles.taskItem, item.completed && styles.completedTask]}
      onPress={() => toggleTask(item.id)}
    >
      <Text style={[styles.taskText, item.completed && styles.completedText]}>
        {item.completed ? '✔' : '•'} {item.title}
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={tasks}
        renderItem={renderTask}
        keyExtractor={(item) => item.id}
        refreshControl={
          <RefreshControl refreshing={loading} onRefresh={loadTasks} />
        }
        ListEmptyComponent={
          <Text style={styles.emptyText}>No tasks yet. Create one in Chat!</Text>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
    padding: 16,
  },
  taskItem: {
    backgroundColor: '#fff',
    padding: 16,
    marginBottom: 8,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#2563eb',
  },
  completedTask: {
    borderLeftColor: '#10b981',
    opacity: 0.7,
  },
  taskText: {
    fontSize: 16,
    color: '#1e293b',
  },
  completedText: {
    textDecorationLine: 'line-through',
    color: '#6b7280',
  },
  emptyText: {
    textAlign: 'center',
    color: '#6b7280',
    fontSize: 16,
    marginTop: 32,
  },
});

export default TasksScreen;