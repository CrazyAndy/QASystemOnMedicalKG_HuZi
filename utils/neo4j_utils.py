from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from utils.logger_utils import info, error

load_dotenv()


class Node:
    def __init__(self, id, labels, properties):
        self.id = id
        self.labels = labels
        self.properties = properties

class Relationship:
    def __init__(self, id, type, properties):
        self.id = id
        self.type = type
        self.properties = properties


class Neo4jUtils:
    """
    Neo4j数据库操作工具类
    
    提供对Neo4j图数据库的增删改查操作，支持节点和关系的管理，
    以及自定义Cypher查询的执行。
    """
    
    def __init__(self):
        """
        初始化Neo4j连接
        
        从环境变量中读取连接配置并创建数据库驱动
        """
        self.uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.username = os.getenv('NEO4J_USERNAME', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'password')
        self.database = os.getenv('NEO4J_DATABASE', 'neo4j')
        
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.username, self.password)
            )
            info(f"Neo4j连接已建立: {self.uri}")
        except Exception as e:
            error(f"Neo4j连接失败: {str(e)}")
            raise
    
    def create_node(self, label, properties=None):
        """
        创建节点
        
        Args:
            label (str): 节点标签
            properties (dict, optional): 节点属性
            
        Returns:
            dict: 包含操作结果的字典
        """
        try:
            with self.driver.session(database=self.database) as session:
                if properties:
                    query = f"CREATE (n:{label} $properties) RETURN n"
                    result = session.run(query, properties=properties)
                else:
                    query = f"CREATE (n:{label}) RETURN n"
                    result = session.run(query)
                
                record = result.single()
                if record:
                    node = record['n']
                    info(f"成功创建节点: {label}")
                    return {
                        'success': True,
                        'node': Node(
                            id=node.id,
                            labels=list(node.labels),
                            properties=dict(node)
                        )
                    }
                else:
                    return {'success': False, 'error': '节点创建失败'}
                    
        except Exception as e:
            error(f"创建节点失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def find_node(self, label, properties=None):
        """
        查找单个节点
        
        Args:
            label (str): 节点标签
            properties (dict, optional): 匹配属性
            
        Returns:
            dict: 包含节点信息或None的字典
        """
        try:
            with self.driver.session(database=self.database) as session:
                if properties:
                    where_clause = " AND ".join([f"n.{key} = ${key}" for key in properties.keys()])
                    query = f"MATCH (n:{label}) WHERE {where_clause} RETURN n"
                    result = session.run(query, **properties)
                else:
                    query = f"MATCH (n:{label}) RETURN n LIMIT 1"
                    result = session.run(query)
                
                record = result.single()
                if record:
                    node = record['n']
                    info(f"找到节点: {label}")
                    return {
                        'success': True,
                        'node': Node(
                            id=node.id,
                            labels=list(node.labels),
                            properties=dict(node)
                        )
                    }
                else:
                    return {'success': True, 'node': None}
                    
        except Exception as e:
            error(f"查找节点失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def find_nodes(self, label, properties=None, limit=None):
        """
        查找多个节点
        
        Args:
            label (str): 节点标签
            properties (dict, optional): 匹配属性
            limit (int, optional): 限制返回数量
            
        Returns:
            dict: 包含节点列表的字典
        """
        try:
            with self.driver.session(database=self.database) as session:
                if properties:
                    where_clause = " AND ".join([f"n.{key} = ${key}" for key in properties.keys()])
                    query = f"MATCH (n:{label}) WHERE {where_clause} RETURN n"
                else:
                    query = f"MATCH (n:{label}) RETURN n"
                
                if limit:
                    query += f" LIMIT {limit}"
                
                result = session.run(query, **properties if properties else {})
                nodes = []
                
                for record in result:
                    node = record['n']
                    nodes.append(Node(
                        id=node.id,
                        labels=list(node.labels),
                        properties=dict(node)
                    ))
                
                info(f"找到 {len(nodes)} 个节点: {label}")
                return {'success': True, 'nodes': nodes}
                    
        except Exception as e:
            error(f"查找节点失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_node(self, label, match_properties, update_properties):
        """
        更新节点属性
        
        Args:
            label (str): 节点标签
            match_properties (dict): 匹配条件
            update_properties (dict): 要更新的属性
            
        Returns:
            dict: 包含操作结果的字典
        """
        try:
            with self.driver.session(database=self.database) as session:
                where_clause = " AND ".join([f"n.{key} = ${key}" for key in match_properties.keys()])
                set_clause = ", ".join([f"n.{key} = ${key}" for key in update_properties.keys()])
                
                query = f"MATCH (n:{label}) WHERE {where_clause} SET {set_clause} RETURN n"
                parameters = {**match_properties, **update_properties}
                
                result = session.run(query, **parameters)
                record = result.single()
                
                if record:
                    node = record['n']
                    info(f"成功更新节点: {label}")
                    return {
                        'success': True,
                        'node': Node(
                            id=node.id,
                            labels=list(node.labels),
                            properties=dict(node)
                        )
                    }
                else:
                    return {'success': False, 'error': '未找到匹配的节点'}
                    
        except Exception as e:
            error(f"更新节点失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_node(self, label, properties):
        """
        删除节点及其所有关系
        
        Args:
            label (str): 节点标签
            properties (dict): 匹配属性
            
        Returns:
            dict: 包含操作结果的字典
        """
        try:
            with self.driver.session(database=self.database) as session:
                where_clause = " AND ".join([f"n.{key} = ${key}" for key in properties.keys()])
                query = f"MATCH (n:{label}) WHERE {where_clause} DETACH DELETE n RETURN count(n) as deleted_count"
                
                result = session.run(query, **properties)
                record = result.single()
                
                if record and record['deleted_count'] > 0:
                    info(f"成功删除 {record['deleted_count']} 个节点: {label}")
                    return {'success': True, 'deleted_count': record['deleted_count']}
                else:
                    return {'success': False, 'error': '未找到匹配的节点'}
                    
        except Exception as e:
            error(f"删除节点失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_relationship(self, from_node, relationship_type, to_node, properties=None):
        """
        创建两个节点之间的关系
        
        Args:
            from_node (Node|dict): 起始节点信息，可以是：
                - Node对象（推荐）
                - {"label": "Person", "properties": {"name": "孙悟空"}}
                - 或者包含完整节点信息的字典（如create_node的返回值）
            relationship_type (str): 关系类型
            to_node (Node|dict): 目标节点信息，格式同from_node
            properties (dict, optional): 关系属性
            
        Returns:
            dict: 包含操作结果的字典
        """
        try:
            with self.driver.session(database=self.database) as session:
                # 处理from_node参数格式
                if isinstance(from_node, Node):
                    # 如果是Node对象
                    from_label = from_node.labels[0]
                    from_properties = from_node.properties
                elif 'node' in from_node:
                    # 如果是create_node返回的格式
                    from_label = from_node['node']['labels'][0]
                    from_properties = from_node['node']['properties']
                else:
                    # 如果是标准格式
                    from_label = from_node['label']
                    from_properties = from_node['properties']
                
                # 处理to_node参数格式
                if isinstance(to_node, Node):
                    # 如果是Node对象
                    to_label = to_node.labels[0]
                    to_properties = to_node.properties
                elif 'node' in to_node:
                    # 如果是create_node返回的格式
                    to_label = to_node['node']['labels'][0]
                    to_properties = to_node['node']['properties']
                else:
                    # 如果是标准格式
                    to_label = to_node['label']
                    to_properties = to_node['properties']
                
                # 构建匹配条件，避免参数名冲突
                from_where_parts = []
                to_where_parts = []
                query_params = {}
                
                # 为from_node的属性添加前缀
                for key, value in from_properties.items():
                    param_name = f"from_{key}"
                    from_where_parts.append(f"a.{key} = ${param_name}")
                    query_params[param_name] = value
                
                # 为to_node的属性添加前缀
                for key, value in to_properties.items():
                    param_name = f"to_{key}"
                    to_where_parts.append(f"b.{key} = ${param_name}")
                    query_params[param_name] = value
                
                # 构建关系创建语句
                if properties:
                    rel_props = ", ".join([f"{key}: ${key}" for key in properties.keys()])
                    create_rel = f"CREATE (a)-[r:{relationship_type} {{{rel_props}}}]->(b)"
                    query_params.update(properties)
                else:
                    create_rel = f"CREATE (a)-[r:{relationship_type}]->(b)"
                
                query = f"""
                MATCH (a:{from_label}), (b:{to_label})
                WHERE {' AND '.join(from_where_parts)} AND {' AND '.join(to_where_parts)}
                {create_rel}
                RETURN r
                """
                
                result = session.run(query, **query_params)
                record = result.single()
                
                if record:
                    rel = record['r']
                    info(f"成功创建关系: {relationship_type}")
                    return {
                        'success': True,
                        'relationship': Relationship(
                            id=rel.id,
                            type=rel.type,
                            properties=dict(rel)
                        )
                    }
                else:
                    return {'success': False, 'error': '未找到匹配的节点'}
                    
        except Exception as e:
            error(f"创建关系失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def find_relationships(self, from_node=None, relationship_type=None, to_node=None):
        """
        查找关系
        
        Args:
            from_node (dict, optional): 起始节点信息
            relationship_type (str, optional): 关系类型
            to_node (dict, optional): 目标节点信息
            
        Returns:
            dict: 包含关系列表的字典
        """
        try:
            with self.driver.session(database=self.database) as session:
                # 构建查询条件
                where_parts = []
                params = {}
                
                # 构建基础查询
                if from_node and to_node:
                    # 有起始节点和目标节点
                    query = f"MATCH (a:{from_node['label']})-[r"
                    if relationship_type:
                        query += f":{relationship_type}"
                    query += f"]->(b:{to_node['label']})"
                    
                    # 添加WHERE条件
                    for key, value in from_node['properties'].items():
                        where_parts.append(f"a.{key} = ${key}")
                        params[key] = value
                    
                    for key, value in to_node['properties'].items():
                        param_name = f"to_{key}"
                        where_parts.append(f"b.{key} = ${param_name}")
                        params[param_name] = value
                        
                elif from_node:
                    # 只有起始节点
                    query = f"MATCH (a:{from_node['label']})-[r"
                    if relationship_type:
                        query += f":{relationship_type}"
                    query += "]->(b)"
                    
                    for key, value in from_node['properties'].items():
                        where_parts.append(f"a.{key} = ${key}")
                        params[key] = value
                        
                elif to_node:
                    # 只有目标节点
                    query = f"MATCH (a)-[r"
                    if relationship_type:
                        query += f":{relationship_type}"
                    query += f"]->(b:{to_node['label']})"
                    
                    for key, value in to_node['properties'].items():
                        where_parts.append(f"b.{key} = ${key}")
                        params[key] = value
                        
                else:
                    # 只按关系类型查询
                    query = "MATCH (a)-[r"
                    if relationship_type:
                        query += f":{relationship_type}"
                    query += "]->(b)"
                
                if where_parts:
                    query += f" WHERE {' AND '.join(where_parts)}"
                
                query += " RETURN r"
                
                result = session.run(query, **params)
                relationships = []
                
                for record in result:
                    rel = record['r']
                    relationships.append(Relationship(
                            id=rel.id,
                            type=rel.type,
                            properties=dict(rel)
                        ))
                
                info(f"找到 {len(relationships)} 个关系")
                return {'success': True, 'relationships': relationships}
                    
        except Exception as e:
            error(f"查找关系失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_relationship(self, from_node, relationship_type, to_node):
        """
        删除指定关系
        
        Args:
            from_node (dict): 起始节点信息
            relationship_type (str): 关系类型
            to_node (dict): 目标节点信息
            
        Returns:
            dict: 包含操作结果的字典
        """
        try:
            with self.driver.session(database=self.database) as session:
                from_where = " AND ".join([f"a.{key} = ${key}" for key in from_node['properties'].keys()])
                to_where = " AND ".join([f"b.{key} = ${key}" for key in to_node['properties'].keys()])
                
                query = f"""
                MATCH (a:{from_node['label']})-[r:{relationship_type}]->(b:{to_node['label']})
                WHERE {from_where} AND {to_where}
                DELETE r
                RETURN count(r) as deleted_count
                """
                
                params = {**from_node['properties'], **to_node['properties']}
                result = session.run(query, **params)
                record = result.single()
                
                if record and record['deleted_count'] > 0:
                    info(f"成功删除 {record['deleted_count']} 个关系: {relationship_type}")
                    return {'success': True, 'deleted_count': record['deleted_count']}
                else:
                    return {'success': False, 'error': '未找到匹配的关系'}
                    
        except Exception as e:
            error(f"删除关系失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def delete_all_nodes_and_relationships(self):
        """
        删除所有节点和关系
        """
        try:
            with self.driver.session(database=self.database) as session:
                session.run("MATCH (n) DETACH DELETE n")
    
                info("成功删除所有节点和关系")
                return {'success': True}
        except Exception as e:
            error(f"删除所有节点和关系失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    
    def run_cypher(self, query, parameters=None):
        """
        执行自定义Cypher查询
        
        Args:
            query (str): Cypher查询语句
            parameters (dict, optional): 查询参数
            
        Returns:
            dict: 包含查询结果的字典
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                records = []
                
                for record in result:
                    records.append(dict(record))
                
                info(f"成功执行Cypher查询，返回 {len(records)} 条记录")
                return {'success': True, 'records': records}
                    
        except Exception as e:
            error(f"执行Cypher查询失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def close(self):
        """
        关闭数据库连接
        """
        try:
            if self.driver:
                self.driver.close()
                info("Neo4j连接已关闭")
        except Exception as e:
            error(f"关闭Neo4j连接失败: {str(e)}")
