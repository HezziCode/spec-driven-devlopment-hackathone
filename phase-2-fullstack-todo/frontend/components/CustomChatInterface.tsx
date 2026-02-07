/**
 * Custom Chat Interface Component
 *
 * A custom chat interface that matches the TaskWave theme and works with our backend API
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { MessageSquare, Plus, Trash2, Send, User, Bot, Menu, X, Loader2 } from 'lucide-react';
import { getAuthToken, useAuth } from '@/lib/auth';
import { parseSSEStream } from '@/lib/sse-parser';
import Link from 'next/link';

// Helper function to render message content with task links
const renderMessageWithTaskLink = (content: string) => {
  // Patterns that indicate a task was created/added
  const taskPatterns = [
    /added.*to your tasks/i,
    /created.*task/i,
    /done!.*added/i,
    /I've added/i,
    /task.*created/i,
    /successfully added/i,
  ];

  const isTaskMessage = taskPatterns.some(pattern => pattern.test(content));

  if (isTaskMessage) {
    return (
      <>
        {content}{' '}
        <Link
          href="/tasks#task-list"
          className="text-cyan-400 hover:text-cyan-300 underline underline-offset-2 font-medium transition-colors"
        >
          See here →
        </Link>
      </>
    );
  }

  return content;
};

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface Thread {
  id: string;
  name: string;
  lastMessage: string;
  lastUpdated: Date;
}

interface ThreadWithNameUpdate {
  id: string;
  name: string;
  lastMessage: string;
  lastUpdated: Date;
  isEditing: boolean;  // Added for thread name editing
}

interface PersistedThreadState {
  userId: string;
  currentThreadId: string | null;
  lastUpdated: string;
}

// localStorage key for thread state persistence
const THREAD_STATE_KEY = 'chatkit_thread_state';

// Save thread state to localStorage
const saveThreadState = (userId: string, threadId: string | null) => {
  try {
    const state: PersistedThreadState = {
      userId,
      currentThreadId: threadId,
      lastUpdated: new Date().toISOString(),
    };
    localStorage.setItem(THREAD_STATE_KEY, JSON.stringify(state));
  } catch (error) {
    console.error('Error saving thread state:', error);
  }
};

// Load thread state from localStorage
const loadThreadState = (userId: string): string | null => {
  try {
    const stored = localStorage.getItem(THREAD_STATE_KEY);
    if (!stored) return null;

    const state: PersistedThreadState = JSON.parse(stored);

    // Verify userId matches (user isolation)
    if (state.userId !== userId) return null;

    return state.currentThreadId;
  } catch (error) {
    console.error('Error loading thread state:', error);
    return null;
  }
};

export function CustomChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false); // Controls input disable state & general loading UI
  const [isStreamingReply, setIsStreamingReply] = useState(false); // Tracks active bot streaming
  const [threads, setThreads] = useState<ThreadWithNameUpdate[]>([]);
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [editingThreadNameId, setEditingThreadNameId] = useState<string | null>(null);
  const [tempThreadName, setTempThreadName] = useState('');
  const [isMobile, setIsMobile] = useState(false);
  const [threadsLoading, setThreadsLoading] = useState(true);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageCountRef = useRef<number>(0);
  const prevIsStreamingReply = useRef<boolean>(false);
  const { session } = useAuth();

  // Mobile detection for responsive layout
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Load threads on component mount and restore last active thread
  useEffect(() => {
    const initializeChat = async () => {
      await loadThreads();

      // Restore last active thread from localStorage
      if (session?.user.id) {
        const lastThreadId = loadThreadState(session.user.id);
        if (lastThreadId) {
          setCurrentThreadId(lastThreadId);
          // loadThreadMessages will be triggered by the currentThreadId useEffect
        }
      }
    };

    initializeChat();
  }, [session?.user.id]);

  // Load messages when thread changes
  useEffect(() => {
    // Should proceed with DB fetch if:
    // 1. Thread ID exists
    // 2. We are NOT currently receiving a streamed response for this thread
    //    (to prevent overwriting live partial data with stale DB data)
    if (currentThreadId && !isStreamingReply) {
      // Determine delay based on streaming state transition
      const wasStreaming = prevIsStreamingReply.current;
      const isPostStreamingTransition = wasStreaming && !isStreamingReply;
      const delay = isPostStreamingTransition ? 500 : 100; // Longer delay for post-streaming to allow backend persistence

      console.log(`⏱️ Scheduling DB fetch: ${isPostStreamingTransition ? 'post-streaming' : 'normal'} (delay: ${delay}ms)`);

      // Load messages from backend for existing thread with retry logic
      const loadWithRetry = async () => {
        try {
          setMessagesLoading(true);
          await loadThreadMessages(currentThreadId);
        } catch (error) {
          console.error('Failed to load thread messages:', error);
          // If thread doesn't exist (404), clear the invalid thread ID
          if (error instanceof Error && error.message.includes('404')) {
            console.log('Thread not found, clearing invalid thread ID');
            setCurrentThreadId(null);
            setMessages([]);
            if (session?.user.id) {
              saveThreadState(session.user.id, null);
            }
          }
        } finally {
          setMessagesLoading(false);
        }
      };

      const timer = setTimeout(() => {
        loadWithRetry();
      }, delay);

      return () => clearTimeout(timer);
    } else if (!currentThreadId) {
      // No thread selected, clear messages
      setMessages([]);
    }

    // Update the previous streaming state ref for next comparison
    prevIsStreamingReply.current = isStreamingReply;
    // We intentionally include all dependencies to ensure state correctness
  }, [currentThreadId, session?.user.id, isStreamingReply]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadThreads = async () => {
    if (!session?.user.id) return;

    try {
      setThreadsLoading(true);
      const token = getAuthToken();
      if (!token) throw new Error('No authentication token');

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/${session.user.id}/chat/threads`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to load threads');

      const data = await response.json();
      const formattedThreads = data.threads.map((thread: any) => ({
        id: thread.id,
        name: thread.name || 'New Chat',
        lastMessage: thread.last_message_preview || 'New chat',
        lastUpdated: new Date(thread.updated_at),
      }));

      setThreads(formattedThreads);
    } catch (error) {
      console.error('Error loading threads:', error);
    } finally {
      setThreadsLoading(false);
    }
  };

  const reconcileMessages = (dbMessages: Message[], localMessages: Message[]): Message[] => {
    console.log('🔍 Reconciling:', {
      dbCount: dbMessages.length,
      localCount: localMessages.length,
      dbMessages: dbMessages.map(m => ({ id: m.id, content: m.content.substring(0, 50) + '...' })),
      localMessages: localMessages.map(m => ({ id: m.id, content: m.content.substring(0, 50) + '...' }))
    });

    // Strategy: DB is source of truth, but we preserve optimistic local messages
    const merged: Message[] = [];
    const seenIds = new Set<string>();

    // Helper to check if message ID looks like a DB ID (not a frontend optimistic ID)
    const isLikelyDbId = (id: string): boolean => {
      // DB IDs are usually UUIDs or numbers, not our pattern
      // Our optimistic IDs: msg_TIMESTAMP_COUNT, msg_TIMESTAMP_COUNT_assistant, error_TIMESTAMP_RANDOM
      // Return true if NOT one of our patterns
      return !(
        id.startsWith('msg_') ||
        id.startsWith('error_')
      );
    };

    // Create a lookup of DB messages by content fingerprint for deduplication
    const dbContentMap = new Map<string, Message>();
    for (const dbMsg of dbMessages) {
      // Simple fingerprint: role + first 100 chars of content
      const fingerprint = `${dbMsg.role}:${dbMsg.content.substring(0, 100)}`;
      if (!dbContentMap.has(fingerprint)) {
        dbContentMap.set(fingerprint, dbMsg);
      }
    }

    // First pass: Add all DB messages (source of truth)
    for (const dbMsg of dbMessages) {
      if (!seenIds.has(dbMsg.id)) {
        merged.push(dbMsg);
        seenIds.add(dbMsg.id);
      }
    }

    // Second pass: Add local optimistic messages that don't duplicate DB content
    for (const localMsg of localMessages) {
      // Skip if already added (by ID)
      if (seenIds.has(localMsg.id)) {
        console.log(`📝 Skipping duplicate local message by ID: ${localMsg.id}`);
        continue;
      }

      // Check if DB has a message with similar content
      const fingerprint = `${localMsg.role}:${localMsg.content.substring(0, 100)}`;
      const similarDbMsg = dbContentMap.get(fingerprint);

      if (similarDbMsg) {
        // DB has equivalent content - prefer DB message (already added in first pass)
        console.log(`📝 Skipping local message (DB has equivalent): ${localMsg.id} -> ${similarDbMsg.id}`);
        continue;
      }

      // This is a truly new optimistic message (or DB hasn't caught up yet)
      merged.push(localMsg);
      seenIds.add(localMsg.id);
    }

    // Sort by timestamp to maintain chronological order
    merged.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());

    console.log('✅ Reconciliation result:', {
      finalCount: merged.length,
      merged: merged.map(m => ({ id: m.id, role: m.role, content: m.content.substring(0, 30) + '...' }))
    });

    return merged;
  };

  const loadThreadMessages = async (threadId: string) => {
    try {
      if (!session?.user.id) {
        console.error('User not authenticated');
        return;
      }

      const token = getAuthToken();
      if (!token) {
        console.error('No authentication token');
        return;
      }

      // Retry mechanism for thread loading with exponential backoff
      let attempts = 0;
      const maxAttempts = 3;
      let delay = 100; // Initial delay in ms

      let response: Response | null = null;
      while (attempts < maxAttempts) {
        try {
          response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/${session.user.id}/chat/threads/${threadId}`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          // If successful or not a 404 error, break the loop
          if (response.ok || response.status !== 404) {
            break;
          }

          attempts++;
          if (attempts < maxAttempts) {
            console.log(`Thread ${threadId} not found, retrying in ${delay}ms (attempt ${attempts}/${maxAttempts})`);
            await new Promise(resolve => setTimeout(resolve, delay));
            delay *= 2; // Exponential backoff
          }
        } catch (fetchError) {
          attempts++;
          if (attempts >= maxAttempts) {
            throw fetchError;
          }
          console.log(`Network error on attempt ${attempts}, retrying in ${delay}ms`);
          await new Promise(resolve => setTimeout(resolve, delay));
          delay *= 2;
        }
      }

      if (!response || !response.ok) {
        if (!response) {
          throw new Error('Failed to get response after maximum retries');
        }
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        const error = new Error(errorData.error || `HTTP error! status: ${response.status}`);
        throw error;
      }

      const data = await response.json();
      // Check if messages exist in the response
      const messagesData = data.messages || [];
      const dbMessages = messagesData.map((msg: any) => ({
        id: msg.id || `msg_${Date.now()}_${Math.random()}`,
        role: msg.role,
        content: msg.content,
        timestamp: new Date(msg.created_at || Date.now()),
      }));

      // Instead of replacing, reconcile DB messages with current local messages
      const reconciledMessages = reconcileMessages(dbMessages, messages);

      // Only update if reconciliation actually changed something
      const hasSameLength = reconciledMessages.length === messages.length;
      const hasSameContent = hasSameLength && reconciledMessages.every((msg, i) =>
        msg.id === messages[i]?.id && msg.content === messages[i]?.content
      );

      if (!hasSameContent) {
        console.log('🔄 Updating messages after reconciliation');
        setMessages(reconciledMessages);
      } else {
        console.log('✅ No changes needed after reconciliation');
      }
    } catch (error) {
      console.error('Error loading thread messages:', error);
      throw error; // Re-throw so the useEffect can handle it
    }
  };

  const createNewThread = async () => {
    try {
      // Check thread count before allowing new thread creation
      if (session?.user.id) {
        const token = getAuthToken();
        if (token) {
          const threadsResponse = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/api/users/${session.user.id}/chat/threads`,
            {
              headers: {
                'Authorization': `Bearer ${token}`,
              },
            }
          );

          if (threadsResponse.ok) {
            const { total } = await threadsResponse.json();
            if (total >= 20) {
              alert('Chat history is full. Delete some conversations to create new ones.');
              return;
            }
          }
        }
      }

      // Don't create thread locally - let backend create it on first message
      // Just clear the current thread and messages
      setCurrentThreadId(null);
      setMessages([]);

      // Clear localStorage thread state
      if (session?.user.id) {
        saveThreadState(session.user.id, null);
      }
    } catch (error) {
      console.error('Error creating new thread:', error);
    }
  };

  const deleteThread = async (threadId: string) => {
    if (!session?.user.id) {
      console.error('User not authenticated');
      return;
    }

    try {
      const token = getAuthToken();
      if (!token) {
        console.error('No authentication token');
        return;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/${session.user.id}/chat/threads/${threadId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      // Remove thread from local state
      setThreads(prev => prev.filter(thread => thread.id !== threadId));

      // If we're deleting the current thread, clear messages and reset current thread
      if (currentThreadId === threadId) {
        setCurrentThreadId(null);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error deleting thread:', error);
      // Show user-friendly error message
      alert(`Failed to delete thread: ${(error as Error).message}`);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading || !session?.user.id) return;

    messageCountRef.current++;
    const userMessage: Message = {
      id: `msg_${Date.now()}_${messageCountRef.current}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    // Add user message to UI immediately
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputValue('');
    setIsLoading(true);
    setIsStreamingReply(true);

    try {
      // Send message to backend - let backend create thread if needed
      const token = getAuthToken();
      if (!token) throw new Error('No authentication token');

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/${session.user.id}/chat/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          thread_id: currentThreadId || null, // null for new threads
          message: inputValue,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      // Check if response is SSE (Server-Sent Events) or JSON
      const contentType = response.headers.get('content-type');
      console.log('🔍 Response content-type:', contentType);

      if (contentType && contentType.includes('text/event-stream')) {
        console.log('✅ SSE streaming detected');
        // Handle streaming response
        const reader = response.body?.getReader();
        if (!reader) throw new Error('No response body');

        const decoder = new TextDecoder();
        let assistantMessageContent = '';
        messageCountRef.current++;
        let assistantMessageId = `msg_${Date.now()}_${messageCountRef.current}_assistant`;
        let receivedThreadId: string | null = null;

        // Create an empty assistant message to populate as we receive data
        setMessages(prev => [
          ...prev,
          {
            id: assistantMessageId,
            role: 'assistant',
            content: '',
            timestamp: new Date(),
          }
        ]);

        let buffer = ''; // Buffer for accumulating SSE data

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          // Append new chunk to buffer
          buffer += decoder.decode(value, { stream: true });
          console.log('📦 Raw buffer (first 200 chars):', buffer.substring(0, 200));
          console.log('📦 Buffer length:', buffer.length);

          // Parse accumulated SSE data using the parser utility
          const chunks = parseSSEStream(buffer);
          console.log('🔧 Parsed chunks count:', chunks.length);
          console.log('🔧 Parsed chunks:', JSON.stringify(chunks, null, 2));

          // Process each parsed chunk
          for (const chunk of chunks) {
            console.log('📝 Processing chunk:', JSON.stringify(chunk));
            console.log('📝 Chunk content:', chunk.content);
            console.log('📝 Chunk content type:', typeof chunk.content);

            // Handle error events separately
            if (chunk.eventType === 'error') {
              console.error('❌ SSE Error received:', chunk.content);

              // Check if this is an API key error (401) and show a more user-friendly message
              if (chunk.content.includes('401') || chunk.content.includes('invalid_api_key')) {
                // Update the assistant message with a user-friendly error
                setMessages(prev => [
                  ...prev,
                  {
                    id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                    role: 'assistant',
                    content: `⚠️ Sorry, there seems to be an issue with the AI service. Please check that your API key is configured correctly.`,
                    timestamp: new Date(),
                  }
                ]);
              } else {
                // Update the assistant message with error content
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMessageId
                      ? { ...msg, content: `⚠️ Error: ${chunk.content}` }
                      : msg
                  ).filter(msg => !(msg.role === 'assistant' && msg.id === assistantMessageId && msg.content === '')) // Remove empty error messages
                );
              }

              // Stop loading state on error
              setIsLoading(false);
              break; // Exit the loop on error
            }

            // Extract clean text content (no protocol artifacts) for non-error events
            if (chunk.content && (!chunk.eventType || (chunk.eventType as string) !== 'error')) {
              assistantMessageContent += chunk.content;
              console.log('✨ Updated content (length):', assistantMessageContent.length);
              console.log('✨ Updated content (first 50 chars):', assistantMessageContent.substring(0, 50));

              // Update the assistant message with clean text
              setMessages(prev =>
                prev.map(msg =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: assistantMessageContent }
                    : msg
                )
              );
            }

            // Handle thread_created event to extract thread_id
            if (chunk.eventType === 'thread_created' && chunk.metadata?.threadId) {
              receivedThreadId = chunk.metadata.threadId;
              console.log('🧵 New thread created:', receivedThreadId);

              // If this is a new thread, create it in the frontend state
              if (!currentThreadId) {
                const newThread: ThreadWithNameUpdate = {
                  id: receivedThreadId,
                  name: inputValue.substring(0, 30) + (inputValue.length > 30 ? '...' : ''),
                  lastMessage: inputValue,
                  lastUpdated: new Date(),
                  isEditing: false,
                };
                setThreads(prev => {
                  // Check if thread already exists to avoid duplicates
                  if (prev.some(t => t.id === receivedThreadId)) {
                    return prev;
                  }
                  return [newThread, ...prev];
                });

                // Set the current thread ID but don't trigger immediate loading
                // The useEffect will handle loading with the delay to prevent race conditions
                setCurrentThreadId(receivedThreadId);

                // Save the thread ID to localStorage for persistence
                if (session?.user.id) {
                  saveThreadState(session.user.id, receivedThreadId);
                }
              }
            }

            // Handle completion event and extract thread_id from metadata
            if (chunk.isComplete && chunk.metadata?.threadId) {
              receivedThreadId = chunk.metadata.threadId;

              // If this is a new thread, create it in the frontend state
              if (!currentThreadId) {
                const newThread: ThreadWithNameUpdate = {
                  id: receivedThreadId,
                  name: inputValue.substring(0, 30) + (inputValue.length > 30 ? '...' : ''),
                  lastMessage: inputValue,
                  lastUpdated: new Date(),
                  isEditing: false,
                };
                setThreads(prev => {
                  // Check if thread already exists to avoid duplicates
                  if (prev.some(t => t.id === receivedThreadId)) {
                    return prev;
                  }
                  return [newThread, ...prev];
                });

                // Set the current thread ID but don't trigger immediate loading
                // The useEffect will handle loading with the delay to prevent race conditions
                setCurrentThreadId(receivedThreadId);

                // Save the thread ID to localStorage for persistence
                if (session?.user.id) {
                  saveThreadState(session.user.id, receivedThreadId);
                }
              }
            }
          }

          // Clear buffer after processing complete events
          // Keep incomplete events in buffer for next iteration
          // Handle both \r\n\r\n (Windows) and \n\n (Unix) event separators
          const windowsEventSeparator = buffer.lastIndexOf('\r\n\r\n');
          const unixEventSeparator = buffer.lastIndexOf('\n\n');
          const lastNewlineIndex = Math.max(windowsEventSeparator, unixEventSeparator);

          if (lastNewlineIndex !== -1) {
            // Clear processed events from buffer
            if (lastNewlineIndex === windowsEventSeparator) {
              buffer = buffer.substring(lastNewlineIndex + 4); // Skip \r\n\r\n
            } else {
              buffer = buffer.substring(lastNewlineIndex + 2); // Skip \n\n
            }
          }
        }
      } else {
        // Handle JSON response
        const data = await response.json();
        const assistantMessage: Message = {
          id: `msg_${Date.now()}_assistant`,
          role: 'assistant',
          content: data.response || 'Received response from server',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);

        // Update thread name after first message if this is the first message in the thread
        if (newMessages.length === 1 && currentThreadId) {
          const threadTitle = inputValue.substring(0, 30) + (inputValue.length > 30 ? '...' : '');
          setThreads(prev =>
            prev.map(thread =>
              thread.id === currentThreadId
                ? { ...thread, name: threadTitle, lastMessage: inputValue.substring(0, 50) + (inputValue.length > 50 ? '...' : '') }
                : thread
            )
          );
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message to the chat with unique ID
      setMessages(prev => [
        ...prev,
        {
          id: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          role: 'assistant',
          content: `Error: ${(error as Error).message}`,
          timestamp: new Date(),
        }
      ]);
    } finally {
      setIsLoading(false);
      setIsStreamingReply(false);
    }
  };

  // Function to start editing a thread name
  const startEditingThreadName = (threadId: string, currentName: string) => {
    setEditingThreadNameId(threadId);
    setTempThreadName(currentName);
  };

  // Function to save the edited thread name
  const saveEditedThreadName = async (threadId: string) => {
    if (!tempThreadName.trim()) {
      cancelEditingThreadName();
      return;
    }

    try {
      if (!session?.user.id) {
        console.error('User not authenticated');
        return;
      }

      const token = getAuthToken();
      if (!token) {
        console.error('No authentication token');
        return;
      }

      // Update the thread name in the backend
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/users/${session.user.id}/chat/threads/${threadId}/sync`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          thread_id: threadId,
          name: tempThreadName.trim(),
          last_message_preview: threads.find(t => t.id === threadId)?.lastMessage || null,
          message_count: messages.length, // This might not be accurate, but we'll update it later
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      // Update the thread name in the local state
      setThreads(prev =>
        prev.map(thread =>
          thread.id === threadId
            ? { ...thread, name: tempThreadName.trim() }
            : thread
        )
      );
    } catch (error) {
      console.error('Error saving thread name:', error);
      alert(`Failed to save thread name: ${(error as Error).message}`);
    } finally {
      setEditingThreadNameId(null);
      setTempThreadName('');
    }
  };

  // Function to cancel editing
  const cancelEditingThreadName = () => {
    setEditingThreadNameId(null);
    setTempThreadName('');
  };

  // Handle Enter key press in the thread name input
  const handleThreadNameKeyDown = (e: React.KeyboardEvent, threadId: string) => {
    if (e.key === 'Enter') {
      saveEditedThreadName(threadId);
    } else if (e.key === 'Escape') {
      cancelEditingThreadName();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-[600px] lg:h-[600px] w-full max-w-full rounded-lg border border-cyan-500/20 shadow-lg shadow-cyan-500/10 bg-slate-900/80 backdrop-blur-sm overflow-hidden relative">
      {/* Mobile Header - Only visible on mobile */}
      {isMobile && (
        <div className="absolute top-0 left-0 right-0 z-30 flex items-center justify-between p-4 border-b border-slate-700/50 bg-slate-900/90 backdrop-blur-md max-w-full">
          <button
            onClick={() => setIsSidebarOpen(true)}
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
            aria-label="Open chat history"
          >
            <Menu className="w-6 h-6 text-cyan-400" />
          </button>
          <span className="text-lg font-semibold text-white">Chat</span>
          <div className="w-[44px]" /> {/* Spacer for centering */}
        </div>
      )}

      {/* Backdrop - Only visible on mobile when sidebar is open */}
      {isMobile && isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsSidebarOpen(false)}
          aria-label="Close sidebar"
        />
      )}

      {/* Sidebar */}
      {(isSidebarOpen || !isMobile) && (
        <div className={`
          ${isMobile ? 'fixed left-0 top-0 bottom-0 z-50' : 'relative'}
          ${isMobile && !isSidebarOpen ? '-translate-x-full' : 'translate-x-0'}
          w-64 bg-slate-900/90 backdrop-blur-md border-r border-slate-700/50 flex flex-col
          transition-transform duration-300 ease-out
        `}>
          <div className="p-4 border-b border-slate-700/50 flex justify-between items-center">
            <button
              onClick={createNewThread}
              className="flex-1 flex items-center justify-between px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition-colors duration-200 mr-2"
            >
              <span className="font-medium">New Chat</span>
              <Plus className="w-4 h-4" />
            </button>
            {isMobile && (
              <button
                onClick={() => setIsSidebarOpen(false)}
                className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
                aria-label="Close sidebar"
              >
                <X className="w-6 h-6 text-slate-400" />
              </button>
            )}
          </div>

          <div className="flex-1 overflow-y-auto p-2">
            <div className="space-y-1">
              {threadsLoading ? (
                // Loading Skeleton for Threads
                Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="p-3 rounded-lg min-h-[44px] animate-pulse">
                    <div className="flex items-center justify-between mb-2">
                      <div className="h-4 bg-slate-700/50 rounded w-24"></div>
                      <div className="h-3 bg-slate-700/50 rounded w-3"></div>
                    </div>
                    <div className="h-3 bg-slate-700/50 rounded w-3/4"></div>
                  </div>
                ))
              ) : (
                threads.map((thread) => (
                  <div
                    key={thread.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors duration-200 group min-h-[44px] ${
                      currentThreadId === thread.id ? 'bg-slate-800/50' : 'hover:bg-slate-800/50'
                    }`}
                    onClick={() => {
                      // Clear messages immediately when switching threads
                      setMessages([]);
                      setCurrentThreadId(thread.id);
                      // Save thread state to localStorage
                      if (session?.user.id) {
                        saveThreadState(session.user.id, thread.id);
                      }
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center truncate">
                        <MessageSquare className="w-4 h-4 text-cyan-400 mr-2 flex-shrink-0" />
                        {editingThreadNameId === thread.id ? (
                          <input
                            type="text"
                            value={tempThreadName}
                            onChange={(e) => setTempThreadName(e.target.value)}
                            onBlur={() => saveEditedThreadName(thread.id)}
                            onKeyDown={(e) => handleThreadNameKeyDown(e, thread.id)}
                            className="text-sm bg-slate-700 text-slate-200 px-1 py-0.5 rounded focus:outline-none focus:ring-1 focus:ring-cyan-500 flex-1 min-w-0"
                            autoFocus
                          />
                        ) : (
                          <span
                            className="text-sm text-slate-200 truncate cursor-pointer hover:bg-slate-700/50 px-1 rounded"
                            onDoubleClick={() => startEditingThreadName(thread.id, thread.name)}
                          >
                            {thread.name}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-1">
                        {editingThreadNameId === thread.id && (
                          <>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                saveEditedThreadName(thread.id);
                              }}
                              className="p-1 hover:bg-slate-600 rounded"
                            >
                              <svg className="w-3 h-3 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                              </svg>
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                cancelEditingThreadName();
                              }}
                              className="p-1 hover:bg-slate-600 rounded"
                            >
                              <svg className="w-3 h-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                              </svg>
                            </button>
                          </>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteThread(thread.id);
                          }}
                          className={`${
                            isMobile ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
                          } p-1 hover:bg-slate-700 rounded transition-all duration-200`}
                          aria-label="Delete thread"
                        >
                          <Trash2 className="w-3 h-3 text-slate-400" />
                        </button>
                      </div>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 truncate">{thread.lastMessage}</p>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="p-4 border-t border-slate-700/50">
            <div className="text-xs text-slate-500 text-center">
              ChatTask AI Assistant
            </div>
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className={`flex-1 flex flex-col w-full max-w-full overflow-x-hidden ${isMobile ? 'pt-16' : ''}`}>
        {/* Toggle sidebar button - Only visible on desktop */}
        {!isMobile && (
          <div className="p-4 border-b border-slate-700/50 flex items-center w-full max-w-full overflow-x-hidden">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="mr-4 p-2 rounded-lg hover:bg-slate-800/50 transition-colors duration-200"
            >
              <MessageSquare className="w-5 h-5 text-cyan-400" />
            </button>
            <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-teal-400">
              ChatTask AI Assistant
            </h1>
          </div>
        )}

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 h-full w-full max-w-full overflow-x-hidden">
          {messagesLoading ? (
             <div className="flex flex-col items-center justify-center h-full">
               <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mb-2" />
               <p className="text-slate-400">Loading conversation...</p>
             </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <MessageSquare className="w-12 h-12 text-cyan-400/50 mb-4" />
              <h3 className="text-lg font-semibold text-slate-300 mb-2">Start a conversation</h3>
              <p className="text-slate-500 max-w-md">
                Ask me anything about your tasks! I can help you create, update, search, and manage your todos.
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-cyan-600/20 to-teal-600/20 border border-cyan-500/30'
                      : 'bg-slate-800/50 border border-slate-700/50'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {message.role === 'assistant' && (
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center">
                        <Bot className="w-3 h-3 text-cyan-400" />
                      </div>
                    )}
                    <div className="flex-1">
                      <div className="text-sm text-slate-200 whitespace-pre-wrap">
                        {message.role === 'assistant'
                          ? renderMessageWithTaskLink(message.content)
                          : message.content}
                      </div>
                    </div>
                    {message.role === 'user' && (
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-teal-500/20 flex items-center justify-center">
                        <User className="w-3 h-3 text-teal-400" />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-lg p-4 bg-slate-800/50 border border-slate-700/50">
                <div className="flex items-center space-x-2">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center">
                    <Bot className="w-3 h-3 text-cyan-400" />
                  </div>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce animation-delay-150"></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce animation-delay-300"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="sticky bottom-0 p-4 border-t border-slate-700/50 bg-slate-900/90 backdrop-blur-md w-full max-w-full overflow-x-hidden">
          <div className="flex space-x-2 w-full max-w-full">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message ChatTask AI..."
              className="flex-1 bg-slate-800/50 border border-slate-700/50 rounded-lg px-4 py-3 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-transparent resize-none"
              rows={2}
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputValue.trim()}
              className="px-4 py-3 bg-gradient-to-r from-cyan-600 to-teal-600 hover:from-cyan-700 hover:to-teal-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-all duration-200 flex items-center justify-center min-h-[44px] min-w-[44px]"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-slate-500 mt-2 text-center">
            ChatTask AI can help you manage your tasks. Be specific with your requests!
          </p>
        </div>
      </div>
    </div>
  );
}