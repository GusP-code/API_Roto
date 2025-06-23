from models.data_model import ResponseModel
from pymongo import MongoClient
from typing import Dict, Any
from config.settings import settings

class DataService:
    @staticmethod
    def get_complete_data(set_id: str, width: int, height: int, include_schraube: bool = False) -> ResponseModel:
        try:
            # Obtener la cadena de conexión de la configuración
            connection_string = settings.DATABASE_URL
            db_name = settings.DATABASE_NAME

            # Llamar a la función find_fittings_for_set
            result = DataService.find_fittings_for_set(
                set_id=set_id,
                width=width,
                height=height,
                connection_string=connection_string,
                db_name=db_name,
                include_schraube=include_schraube
            )

            # Verificar si hay errores
            if "error" in result:
                raise Exception(result["error"])

            # Verificar si hay kits faltantes
            if "missing_kits" in result and result["missing_kits"]:
                raise Exception(f"Kits no encontrados: {', '.join(result['missing_kits'])}")

            # Verificar si hay dimensiones inválidas
            if "dimension_errors" in result and result["dimension_errors"]:
                errors = [f"Kit {e['kit_id']}: {e['error']}" for e in result["dimension_errors"]]
                raise Exception(f"Errores en dimensiones: {'; '.join(errors)}")

            # Verificar si hay kits sin fittings aplicables
            if "kits_without_applicable_fittings" in result and result["kits_without_applicable_fittings"]:
                raise Exception(f"Kits sin fittings aplicables: {', '.join(result['kits_without_applicable_fittings'])}")

            # Verificar si no hay fittings
            if result["total_fittings"] == 0:
                raise Exception("No se encontraron fittings que cumplan con las dimensiones especificadas")

            # Asegurarse de que todos los campos requeridos estén presentes
            if not isinstance(result.get("applicable_fittings"), list):
                raise Exception("Error en el formato de los fittings")

            # Convertir el resultado al modelo
            try:
                return ResponseModel(**result)
            except Exception as model_error:
                print(f"Error al convertir al modelo: {str(model_error)}")
                raise Exception(f"Error al procesar los datos: {str(model_error)}")

        except Exception as e:
            print(f"Error en get_complete_data: {str(e)}")
            raise Exception(f"Error al consultar MongoDB: {str(e)}")

    @staticmethod
    def find_fittings_for_set(set_id, width, height, connection_string, db_name="kits_db", include_schraube=False):
        client = MongoClient(connection_string)
        try:
            db = client[db_name]
            sets_collection = db["sets_collection"]
            kits_collection = db["kits_collection"]
            fittings_collection = db["fittings_collection"] 
            colour_maps_collection = db["colour_maps_collection"] 
        
            # Resultado
            result = {
                "set_id": set_id,
                "width": width,
                "height": height,
                "applicable_fittings": [],
                "options_summary": {}
            }
            
            # Para rastrear opciones, alternatives y colores
            all_used_options = {}
            all_used_alternatives = set()  
            all_used_colors = set() 

            # Función para registrar opciones utilizadas
            def register_options(options_list):
                if not isinstance(options_list, list):
                    return
                    
                for option in options_list:
                    if isinstance(option, dict) and 'name' in option and 'value' in option:
                        option_name = option['name']
                        option_value = str(option['value'])  # Convertir a string para consistencia
                        
                        # Inicializar la lista de valores para esta opción si no existe
                        if option_name not in all_used_options:
                            all_used_options[option_name] = set()
                        
                        # Añadir el valor a la lista de valores únicos
                        all_used_options[option_name].add(option_value)

            # Función para obtener colores disponibles para una referencia
            def get_colors_for_ref(ref):
                try:
                    colour_maps = colour_maps_collection.find({"articles.ref": ref})
                    colors_list = []   
                    for colour_map in colour_maps:
                        filtered_articles = [article for article in colour_map.get("articles", []) if article["ref"] == ref]
                        if filtered_articles:
                            color_name = colour_map.get("name", "")
                            colors_list.append({
                                "name": color_name,
                                "articles": filtered_articles
                            })
                            # Registrar el color encontrado
                            if color_name:
                                all_used_colors.add(color_name)
                    return colors_list if colors_list else None
                except Exception as e:
                    print(f"Error al obtener colores para ref {ref}: {str(e)}")
                    return None

            # Función recursiva para procesar artículos y sus derivados
            def process_article_fittings(article_ref, parent_info=None, depth=0, max_depth=5):
                if depth >= max_depth:
                    print(f"Alcanzada profundidad máxima de recursión ({max_depth}) para el artículo {article_ref}")
                    return []
                
                if article_ref == "Schraube" and parent_info:
                    if not include_schraube:
                        return []

                try:
                    article_fitting_doc = fittings_collection.find_one({"ref": article_ref})
                    if not article_fitting_doc:
                        return []
                    
                    article_fitting = {
                        "fitting_id": str(article_fitting_doc.get("_id", "")),
                        "ref": article_ref,
                        "description": article_fitting_doc.get("description", ""),    
                        "fittingType": article_fitting_doc.get("fittingType", ""),
                        "location": article_fitting_doc.get("location", ""),
                        "handUseable": bool(article_fitting_doc.get("handUseable", False))
                    }
                    
                    colors = get_colors_for_ref(article_ref)
                    if colors:
                        article_fitting["colors"] = colors

                    if parent_info:
                        article_fitting["parent_info"] = parent_info
                        # Registrar opciones del parent_info si existen 
                        if "options" in parent_info:
                            register_options(parent_info["options"])

                        # Registrar alternative del parent_info
                        if "set_description" in parent_info and "alternative" in parent_info["set_description"]:
                            alt_value = parent_info["set_description"].get("alternative")
                            if alt_value:
                                all_used_alternatives.add(str(alt_value))
                    
                    derived_fittings = []
                    
                    if "generation" in article_fitting_doc:
                        generation = article_fitting_doc["generation"]
                        
                        if "articles" in generation:
                            articles_list = generation["articles"]
                            article_fitting["articles"] = articles_list

                            # Registrar opciones de los artículos si existen
                            for article in articles_list:
                                if "options" in article:
                                    register_options(article["options"])
                            
                            for derived_article in articles_list:
                                derived_article_ref = derived_article.get("ref", "")
                                if derived_article_ref:
                                    current_parent_info = {
                                        "parent_fitting_id": article_fitting.get("fitting_id", ""),
                                        "parent_ref": article_ref,
                                        "location": derived_article.get("location", ""),
                                        "side": derived_article.get("side", ""),
                                        "options": derived_article.get("options", [])
                                    }
                                    
                                    derived_results = process_article_fittings(
                                        derived_article_ref, 
                                        current_parent_info, 
                                        depth + 1, 
                                        max_depth
                                    )
                                    derived_fittings.extend(derived_results)
                        
                        if "operations" in generation:
                            article_fitting["operations"] = generation["operations"]
                    
                    return [article_fitting] + derived_fittings
                except Exception as e:
                    print(f"Error al procesar artículo {article_ref}: {str(e)}")
                    return []

            # 1. Buscar el set
            set_doc = sets_collection.find_one({"_id": set_id})
            if not set_doc:
                raise Exception(f"No se encontró el set con ID: {set_id}")

            # 2. Verificar dimensiones
            try:
                min_width = int(set_doc.get("minWidth", 0))
                max_width = int(set_doc.get("maxWidth", 0))
                min_height = int(set_doc.get("minHeight", 0))
                max_height = int(set_doc.get("maxHeight", 0))
                
                if not (min_width <= width <= max_width and min_height <= height <= max_height):
                    raise Exception(f"Las dimensiones proporcionadas (ancho: {width}, alto: {height}) están fuera del rango del set (ancho: {min_width}-{max_width}, alto: {min_height}-{max_height})")
            except ValueError:
                raise Exception(f"Error al procesar las dimensiones del set {set_id}")

            # 3. Procesar kits
            missing_kits = []
            dimension_errors = []
            kits_without_applicable_fittings = []

            if "kits" in set_doc:
                for kit_info in set_doc["kits"]:
                    kit_id = kit_info.get("kit_id")
                    kit_doc = kits_collection.find_one({"_id": kit_id})
                    if not kit_doc:
                        missing_kits.append(kit_id)
                        continue

                    applicable_desc_found = False
                    if "set_descriptions" in kit_doc:
                        for set_desc in kit_doc["set_descriptions"]:
                            try:
                                set_min_width = int(set_desc.get("minWidth", 0))
                                set_max_width = int(set_desc.get("maxWidth", 0))
                                set_min_height = int(set_desc.get("minHeight", 0))
                                set_max_height = int(set_desc.get("maxHeight", 0))
                                
                                if (set_min_width <= width <= set_max_width and 
                                    set_min_height <= height <= set_max_height):
                                    fitting_id = set_desc.get("fittingId")
                                    if fitting_id:
                                        fitting_doc = fittings_collection.find_one({"_id": fitting_id})
                                        if fitting_doc:
                                            applicable_desc_found = True
                                            fitting_result = {
                                                "fitting_id": str(fitting_id),
                                                "ref": fitting_doc.get("ref", ""),
                                                "description": fitting_doc.get("description", ""),
                                                "fittingType": fitting_doc.get("fittingType", ""),
                                                "location": fitting_doc.get("location", ""),
                                                "handUseable": bool(fitting_doc.get("handUseable", False)),
                                                "set_description": {
                                                    "position": set_desc.get("position", ""),
                                                    "referencePoint": set_desc.get("referencePoint", "")
                                                }
                                            }

                                            fitting_ref = fitting_doc.get("ref", "")
                                            colors = get_colors_for_ref(fitting_ref)
                                            if colors:
                                                fitting_result["colors"] = colors

                                            optional_attributes = ["inverted", "x", "alternative"]
                                            for attr in optional_attributes:
                                                if attr in set_desc:
                                                    fitting_result["set_description"][attr] = set_desc.get(attr, "")
                                                    if attr == "alternative" and set_desc.get(attr):
                                                        all_used_alternatives.add(str(set_desc.get(attr)))
                                            
                                            if "options" in set_desc:
                                                fitting_result["set_description"]["options"] = set_desc.get("options", [])
                                                register_options(set_desc.get("options", []))

                                            articles_list = []
                                            if "generation" in fitting_doc:
                                                generation = fitting_doc["generation"]
                                                
                                                if "articles" in generation:
                                                    articles_list = generation["articles"]
                                                    for article in articles_list:
                                                        article_ref = article.get("ref", "")
                                                        if article_ref:
                                                            colors = get_colors_for_ref(article_ref)
                                                            if colors:
                                                                article["colors"] = colors

                                                            if "options" in article:
                                                                register_options(article["options"])

                                                    fitting_result["articles"] = generation["articles"]
                                
                                                if "operations" in generation:
                                                    fitting_result["operations"] = generation["operations"]
                                            
                                            result["applicable_fittings"].append(fitting_result)

                                            for article in articles_list:
                                                article_ref = article.get("ref", "")
                                                if article_ref:
                                                    parent_info = {
                                                        "parent_fitting_id": fitting_id,
                                                        "parent_ref": fitting_doc.get("ref", ""),
                                                        "location": article.get("location", ""),
                                                        "side": article.get("side", ""),
                                                        "options": article.get("options", []),
                                                        "set_description": fitting_result["set_description"]
                                                    }
                                                    
                                                    derived_fittings = process_article_fittings(article_ref, parent_info)
                                                    
                                                    for derived_fitting in derived_fittings:
                                                        if "set_description" not in derived_fitting:
                                                            derived_fitting["set_description"] = fitting_result["set_description"]
                                                        result["applicable_fittings"].append(derived_fitting)

                            except ValueError as e:
                                dimension_errors.append({
                                    "kit_id": kit_id,
                                    "set_description_id": set_desc.get("id", ""),
                                    "error": str(e)
                                })

                    if not applicable_desc_found:
                        kits_without_applicable_fittings.append(kit_id)

            # Verificar errores y lanzar excepciones si es necesario
            if missing_kits:
                raise Exception(f"Kits no encontrados: {', '.join(missing_kits)}")

            if dimension_errors:
                errors = [f"Kit {e['kit_id']}: {e['error']}" for e in dimension_errors]
                raise Exception(f"Errores en dimensiones: {'; '.join(errors)}")

            if kits_without_applicable_fittings:
                raise Exception(f"Kits sin fittings aplicables: {', '.join(kits_without_applicable_fittings)}")

            total_fittings = len(result.get("applicable_fittings", []))
            result["total_fittings"] = total_fittings

            if total_fittings == 0:
                raise Exception("No se encontraron fittings que cumplan con las dimensiones especificadas")

            # Añadir el resumen de opciones al resultado 
            for option_name, option_values in all_used_options.items():
                sorted_values = sorted(list(option_values))
                result["options_summary"][option_name] = sorted_values

            # Añadir los valores "alternative" como una opción más en options_summary
            if all_used_alternatives:
                result["options_summary"]["alternative"] = sorted(list(all_used_alternatives))
                
            # Añadir los valores de colores como una opción más en options_summary
            if all_used_colors:
                result["options_summary"]["colors"] = sorted(list(all_used_colors))

            return result

        except Exception as e:
            print(f"Error en find_fittings_for_set: {str(e)}")
            raise Exception(f"Error al procesar los datos: {str(e)}")
        finally:
            client.close()