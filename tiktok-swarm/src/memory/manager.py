"""Memory management utilities for cross-thread persistence"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import Json, RealDictCursor
from src.database.config import get_base_connection_params


class MemoryManager:
    """Manages long-term memory storage across threads"""
    
    def __init__(self):
        self.conn_params = get_base_connection_params()
    
    def _get_connection(self):
        """Get a database connection"""
        return psycopg2.connect(**self.conn_params, cursor_factory=RealDictCursor)
    
    def store_user_preference(self, user_id: str, key: str, value: Any) -> bool:
        """Store a user preference that persists across conversations"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO langgraph_store (namespace, key, value)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (namespace, key) 
                        DO UPDATE SET value = %s, updated_at = CURRENT_TIMESTAMP
                    """, (
                        ["user_preferences", user_id],
                        key,
                        Json(value),
                        Json(value)
                    ))
                    conn.commit()
            return True
        except Exception as e:
            print(f"Error storing user preference: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get all preferences for a user"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT key, value 
                        FROM langgraph_store 
                        WHERE namespace = %s
                    """, (["user_preferences", user_id],))
                    
                    preferences = {}
                    for row in cursor.fetchall():
                        preferences[row['key']] = row['value']
                    return preferences
        except Exception as e:
            print(f"Error getting user preferences: {e}")
            return {}
    
    def store_trend_data(self, trend_type: str, data: Dict[str, Any]) -> bool:
        """Store trending data for analysis"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    key = f"{trend_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    cursor.execute("""
                        INSERT INTO langgraph_store (namespace, key, value)
                        VALUES (%s, %s, %s)
                    """, (
                        ["trends", trend_type],
                        key,
                        Json(data)
                    ))
                    conn.commit()
            return True
        except Exception as e:
            print(f"Error storing trend data: {e}")
            return False
    
    def get_recent_trends(self, trend_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent trend data"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT value, created_at 
                        FROM langgraph_store 
                        WHERE namespace = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (["trends", trend_type], limit))
                    
                    trends = []
                    for row in cursor.fetchall():
                        trend_data = row['value']
                        trend_data['stored_at'] = row['created_at'].isoformat()
                        trends.append(trend_data)
                    return trends
        except Exception as e:
            print(f"Error getting trends: {e}")
            return []
    
    def store_video_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """Store a successful video template for reuse"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO langgraph_store (namespace, key, value)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (namespace, key) 
                        DO UPDATE SET value = %s, updated_at = CURRENT_TIMESTAMP
                    """, (
                        ["video_templates"],
                        template_id,
                        Json(template_data),
                        Json(template_data)
                    ))
                    conn.commit()
            return True
        except Exception as e:
            print(f"Error storing video template: {e}")
            return False
    
    def get_video_templates(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get stored video templates, optionally filtered by category"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    if category:
                        cursor.execute("""
                            SELECT key, value 
                            FROM langgraph_store 
                            WHERE namespace = %s
                            AND value->>'category' = %s
                            ORDER BY updated_at DESC
                        """, (["video_templates"], category))
                    else:
                        cursor.execute("""
                            SELECT key, value 
                            FROM langgraph_store 
                            WHERE namespace = %s
                            ORDER BY updated_at DESC
                        """, (["video_templates"],))
                    
                    templates = []
                    for row in cursor.fetchall():
                        template = row['value']
                        template['template_id'] = row['key']
                        templates.append(template)
                    return templates
        except Exception as e:
            print(f"Error getting video templates: {e}")
            return []
    
    def search_memory(self, namespace: List[str], search_term: str) -> List[Dict[str, Any]]:
        """Search memory by content"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT key, value 
                        FROM langgraph_store 
                        WHERE namespace = %s
                        AND value::text ILIKE %s
                        ORDER BY updated_at DESC
                    """, (namespace, f"%{search_term}%"))
                    
                    results = []
                    for row in cursor.fetchall():
                        results.append({
                            'key': row['key'],
                            'value': row['value']
                        })
                    return results
        except Exception as e:
            print(f"Error searching memory: {e}")
            return []
    
    def clear_old_data(self, namespace: List[str], days_to_keep: int = 30) -> int:
        """Clear data older than specified days"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        DELETE FROM langgraph_store 
                        WHERE namespace = %s
                        AND updated_at < CURRENT_TIMESTAMP - INTERVAL '%s days'
                    """, (namespace, days_to_keep))
                    deleted = cursor.rowcount
                    conn.commit()
                    return deleted
        except Exception as e:
            print(f"Error clearing old data: {e}")
            return 0


# Singleton instance
memory_manager = MemoryManager()