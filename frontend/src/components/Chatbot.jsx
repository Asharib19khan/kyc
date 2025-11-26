import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot } from 'lucide-react';

const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { id: 1, text: "Hi! I'm your KYC Assistant. How can I help you today?", sender: 'bot' }
    ]);
    const [input, setInput] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { id: messages.length + 1, text: input, sender: 'user' };
        setMessages([...messages, userMessage]);
        setInput('');

        // Simulate AI Response
        setTimeout(() => {
            let botResponse = "I'm not sure about that. Can you please contact support?";
            const lowerInput = input.toLowerCase();

            if (lowerInput.includes('verify') || lowerInput.includes('verification')) {
                botResponse = "To verify your identity, go to the 'Verifications' tab and upload your CNIC and a selfie.";
            } else if (lowerInput.includes('loan') || lowerInput.includes('limit')) {
                botResponse = "Loan limits are calculated based on your risk score and income. You can check your eligibility in the 'Loan Management' section.";
            } else if (lowerInput.includes('document') || lowerInput.includes('upload')) {
                botResponse = "Please ensure your documents are clear and not blurry. We accept JPEG and PNG formats.";
            } else if (lowerInput.includes('hello') || lowerInput.includes('hi')) {
                botResponse = "Hello! How can I assist you with your KYC process?";
            }

            setMessages(prev => [...prev, { id: prev.length + 1, text: botResponse, sender: 'bot' }]);
        }, 1000);
    };

    return (
        <div className="fixed bottom-6 right-6 z-50">
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-transform hover:scale-110 flex items-center justify-center"
                >
                    <MessageSquare size={24} />
                </button>
            )}

            {isOpen && (
                <div className="bg-white dark:bg-slate-800 w-80 sm:w-96 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col h-[500px] transition-all animate-in slide-in-from-bottom-10 fade-in">
                    {/* Header */}
                    <div className="bg-blue-600 p-4 flex justify-between items-center">
                        <div className="flex items-center gap-2 text-white">
                            <Bot size={20} />
                            <span className="font-bold">KYC Assistant</span>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="text-blue-100 hover:text-white transition-colors">
                            <X size={20} />
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-50 dark:bg-slate-900/50">
                        {messages.map((msg) => (
                            <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${msg.sender === 'user'
                                        ? 'bg-blue-600 text-white rounded-br-none'
                                        : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-bl-none shadow-sm'
                                    }`}>
                                    {msg.text}
                                </div>
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <form onSubmit={handleSend} className="p-4 bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 flex gap-2">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type a message..."
                            className="flex-1 px-4 py-2 rounded-full border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim()}
                            className="bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <Send size={18} />
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
};

export default Chatbot;
