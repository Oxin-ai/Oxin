from sqlalchemy.orm import Session
from bolna.auth.database import SessionLocal
from bolna.voice_management.models import Voice
from bolna.helpers.logger_config import configure_logger

logger = configure_logger(__name__)

def seed_all_voices():
    """Seed database with all predefined voices."""
    try:
        db = SessionLocal()
        
        # Check if voices already exist
        existing_voices = db.query(Voice).count()
        if existing_voices > 0:
            logger.info("Voices already exist in database")
            return
        
        voices_data = [
            {"id": "02d3c38e-02c5-4068-b521-3a7b9f732832", "provider": "elevenlabs", "name": "Nila - Warm, Natural Tamil Customer Care Agent", "model": "eleven_turbo_v2_5", "voice_id": "V9LCAAi4tTlqe9JadbCo", "accent": "Middle Aged Female Standard Tamil"},
            {"id": "03909666-5ae1-473d-a27b-0229e40b1603", "provider": "inworld", "name": "Olivia", "model": "inworld-tts-1", "voice_id": "Olivia", "accent": ""},
            {"id": "072b4d87-7c97-42bb-a3a8-53654eba1df7", "provider": "sarvam", "name": "Manisha", "model": "bulbul:v2", "voice_id": "manisha", "accent": "Indian Female Kannada"},
            {"id": "0fc22fc1-6546-4d11-9957-6dbb5f8e7caf", "provider": "sarvam", "name": "Arya", "model": "bulbul:v2", "voice_id": "arya", "accent": "Indian female bengali"},
            {"id": "109ba4c4-0219-4b57-8569-bc0d90fa74ee", "provider": "sarvam", "name": "Abhilash", "model": "bulbul:v2", "voice_id": "abhilash", "accent": "Indian Male Malayalam"},
            {"id": "10c82ccc-505b-428b-8acf-1438cd0adeda", "provider": "inworld", "name": "Xinyi", "model": "inworld-tts-1", "voice_id": "Xinyi", "accent": ""},
            {"id": "151a2557-5ac2-4cd0-8c49-0475f1251b49", "provider": "inworld", "name": "Ronald", "model": "inworld-tts-1", "voice_id": "Ronald", "accent": ""},
            {"id": "15700f67-85b6-4d6f-b3d5-35912a895f5e", "provider": "inworld", "name": "Yoona", "model": "inworld-tts-1", "voice_id": "Yoona", "accent": ""},
            {"id": "171954d9-859b-4bd7-ab55-28f4e0caef4f", "provider": "rime", "name": "Tauro", "model": "arcana", "voice_id": "tauro", "accent": "Middle Male US"},
            {"id": "17657b1d-7a8b-4a2b-800b-23cd4122e787", "provider": "sarvam", "name": "Karun", "model": "bulbul:v2", "voice_id": "karun", "accent": "Indian Male Tamil"},
            {"id": "198c76e5-9862-4d4c-823b-0a034249b69d", "provider": "sarvam", "name": "Arya", "model": "bulbul:v2", "voice_id": "arya", "accent": "Indian female telugu"},
            {"id": "19be85eb-dd53-4798-a8c3-1f1a360542f4", "provider": "sarvam", "name": "Manisha", "model": "bulbul:v2", "voice_id": "manisha", "accent": "Indian female punjabi"},
            {"id": "1aa04e4c-e9c9-44ea-8aee-7c61495071f4", "provider": "inworld", "name": "Lennart", "model": "inworld-tts-1", "voice_id": "Lennart", "accent": ""},
            {"id": "1be42dcd-d5a8-4204-9c24-9ea46ea87006", "provider": "sarvam", "name": "Vidya", "model": "bulbul:v2", "voice_id": "vidya", "accent": "Indian female bengali"},
            {"id": "1d86a5dc-c372-45c1-a9d6-04dbc50a2f46", "provider": "inworld", "name": "Szymon", "model": "inworld-tts-1", "voice_id": "Szymon", "accent": ""},
            {"id": "1de60824-b8e2-4782-b11d-371be27966c3", "provider": "inworld", "name": "Ashley", "model": "inworld-tts-1", "voice_id": "Ashley", "accent": ""},
            {"id": "1f0349a8-55be-4400-8e38-7e80939f2589", "provider": "sarvam", "name": "Manisha", "model": "bulbul:v2", "voice_id": "manisha", "accent": "Indian Female Tamil"},
            {"id": "23219405-ca18-4b6b-a804-1371121c7a7c", "provider": "smallest", "name": "Kartik", "model": "lightning-v2", "voice_id": "kartik", "accent": "Indian male kannada"},
            {"id": "247ea53a-f802-4687-b066-c896c06de5a8", "provider": "smallest", "name": "Vidya", "model": "lightning-v2", "voice_id": "vidya", "accent": "Indian female tamil"},
            {"id": "26b45eaf-c3e9-47f2-877b-b18ceb4da121", "provider": "polly", "name": "Danielle", "model": "neural", "voice_id": "Danielle", "accent": "United States (English)"},
            {"id": "26e9bba6-c554-42d3-9dc3-6b82f3e0942b", "provider": "sarvam", "name": "Hitesh", "model": "bulbul:v2", "voice_id": "hitesh", "accent": "Indian Male Malayalam"},
            {"id": "282ddf19-d10a-455c-9e41-900e00a5584f", "provider": "sarvam", "name": "Hitesh", "model": "bulbul:v2", "voice_id": "hitesh", "accent": "Indian Male"},
            {"id": "28d0de06-b536-4194-9b2a-7998871cd97d", "provider": "inworld", "name": "Jing", "model": "inworld-tts-1", "voice_id": "Jing", "accent": ""},
            {"id": "2bd66835-63e8-4cae-9b6e-bef2991f2a89", "provider": "sarvam", "name": "Abhilash", "model": "bulbul:v2", "voice_id": "abhilash", "accent": "Indian male bengali"},
            {"id": "2cc7d4b5-a381-4258-9545-bde2b9a3c369", "provider": "inworld", "name": "Hades", "model": "inworld-tts-1", "voice_id": "Hades", "accent": ""},
            {"id": "2e10b34e-4bcb-4ec5-af66-0a7f6124384b", "provider": "rime", "name": "Astra", "model": "arcana", "voice_id": "astra", "accent": "Young Female US"},
            {"id": "2f74ca9e-c9d8-4002-8154-3ea8a41d0e72", "provider": "sarvam", "name": "Abhilash", "model": "bulbul:v2", "voice_id": "abhilash", "accent": "Indian male punjabi"},
            {"id": "3095339d-cbc2-4d51-9500-67d8c6f159d7", "provider": "sarvam", "name": "Abhilash", "model": "bulbul:v2", "voice_id": "abhilash", "accent": "Indian male english"},
            {"id": "30ac41c7-2adb-4ab3-95bf-da66bbbed0b1", "provider": "rime", "name": "Yadira", "model": "mistv2", "voice_id": "yadira", "accent": "Young Female US"},
            {"id": "30ea1983-6c34-4bef-8e6a-fdeca20b85e8", "provider": "elevenlabs", "name": "Charlie", "model": "eleven_turbo_v2_5", "voice_id": "IKne3meq5aSn9XLyUdCD", "accent": "australian"},
            {"id": "315e34c6-591a-4dd9-b1ea-ce2e4fd2eb42", "provider": "sarvam", "name": "Hitesh", "model": "bulbul:v2", "voice_id": "hitesh", "accent": "Indian Male Kannada"},
            {"id": "3236a248-615b-44ab-bed7-69246555b714", "provider": "rime", "name": "Luna", "model": "arcana", "voice_id": "luna", "accent": "Young Female US"},
            {"id": "3465f779-f667-4922-90d1-5bc44e2c052c", "provider": "sarvam", "name": "Karun", "model": "bulbul:v2", "voice_id": "karun", "accent": "Indian male telugu"},
            {"id": "359e2a79-1a25-4056-b7a6-617e9b99d312", "provider": "rime", "name": "Andromeda", "model": "arcana", "voice_id": "andromeda", "accent": "Young Female US"},
            {"id": "35b65386-44c0-40fc-a2a7-9512ff9dfbe3", "provider": "sarvam", "name": "Arya", "model": "bulbul:v2", "voice_id": "arya", "accent": "Indian Female Malayalam"},
            {"id": "35d94e80-2f51-49e1-bbd2-88c0c56a7cfc", "provider": "inworld", "name": "Shaun", "model": "inworld-tts-1", "voice_id": "Shaun", "accent": ""},
            {"id": "35fc0e77-b7ec-4b9c-a254-460ff9e59e9a", "provider": "elevenlabs", "name": "Sheps Rocky", "model": "eleven_turbo_v2_5", "voice_id": "d5xU2Rwln0n15oHMmaTU", "accent": "american"},
            {"id": "3b7af250-0e6c-449c-af6a-3dcda37770df", "provider": "sarvam", "name": "Arya", "model": "bulbul:v2", "voice_id": "arya", "accent": "Indian Female Tamil"},
            {"id": "4081d565-0520-4c20-a170-1cc8df1a0a2a", "provider": "rime", "name": "Celeste", "model": "arcana", "voice_id": "celeste", "accent": "Middle Female US"},
            {"id": "40f66a68-6532-4a59-959a-6e8a43328ae7", "provider": "elevenlabs", "name": "Lily", "model": "eleven_turbo_v2_5", "voice_id": "pFZP5JQG7iQjIQuC4Bku", "accent": "british"},
            {"id": "433d893f-a639-4634-a7da-25a26f430dbb", "provider": "sarvam", "name": "Abhilash", "model": "bulbul:v2", "voice_id": "abhilash", "accent": "Indian Male"},
            {"id": "4608cc01-bcf4-4f52-abe5-befb0dc928ec", "provider": "sarvam", "name": "Hitesh", "model": "bulbul:v2", "voice_id": "hitesh", "accent": "Indian male english"},
            {"id": "47fe11a6-c8cf-4e15-9691-a470f2ff290f", "provider": "inworld", "name": "Étienne", "model": "inworld-tts-1", "voice_id": "Étienne", "accent": ""},
            {"id": "4a4f8b97-bdc7-4554-a7b6-5a3ba2a9f946", "provider": "sarvam", "name": "Anushka", "model": "bulbul:v2", "voice_id": "anushka", "accent": "Indian female gujarati"},
            {"id": "4b76f188-7bfe-43fe-9a9f-648b494f81d4", "provider": "rime", "name": "Estelle", "model": "arcana", "voice_id": "estelle", "accent": "Middle Female US"},
            {"id": "4d997405-e8e1-47a1-924a-ae5598dc759a", "provider": "sarvam", "name": "Anushka", "model": "bulbul:v2", "voice_id": "anushka", "accent": "Indian female bengali"},
            {"id": "4eb4c330-4438-4994-95e2-bd9f591a850a", "provider": "rime", "name": "Orion", "model": "arcana", "voice_id": "orion", "accent": "Older Male US"},
            {"id": "50b68769-081d-4984-8f30-2b5f96d959a1", "provider": "sarvam", "name": "Vidya", "model": "bulbul:v2", "voice_id": "vidya", "accent": "Indian female telugu"},
            {"id": "50e469c7-ef7e-43d0-af9c-668e3dda4257", "provider": "inworld", "name": "Diego", "model": "inworld-tts-1", "voice_id": "Diego", "accent": ""},
            {"id": "511127e2-f5d0-4347-ad0d-1677a6293af6", "provider": "sarvam", "name": "Manisha", "model": "bulbul:v2", "voice_id": "manisha", "accent": "Indian female bengali"},
            {"id": "53fd48e4-3745-400c-b4c0-e6d9687e78df", "provider": "sarvam", "name": "Manisha", "model": "bulbul:v2", "voice_id": "manisha", "accent": "Indian female gujarati"},
            {"id": "54b63bf7-7605-4e3e-95e5-e6a888ba7c68", "provider": "inworld", "name": "Deborah", "model": "inworld-tts-1", "voice_id": "Deborah", "accent": ""},
            {"id": "5758363a-93b9-4aa9-97f7-31218ab62ab0", "provider": "inworld", "name": "Julia", "model": "inworld-tts-1", "voice_id": "Julia", "accent": ""},
            {"id": "5812996f-a63f-4d31-9e8c-b88311d672bc", "provider": "sarvam", "name": "Karun", "model": "bulbul:v2", "voice_id": "karun", "accent": "Indian male english"},
            {"id": "582b01f2-7a12-4397-aff7-32015f99f641", "provider": "sarvam", "name": "Manisha", "model": "bulbul:v2", "voice_id": "manisha", "accent": "Indian female english"},
            {"id": "5b08ac1a-c066-4274-bccb-a3b0ade247de", "provider": "sarvam", "name": "Hitesh", "model": "bulbul:v2", "voice_id": "hitesh", "accent": "Indian male gujarati"},
            {"id": "5c9db9ea-f3de-4619-a6af-eb56eeec1280", "provider": "inworld", "name": "Priya", "model": "inworld-tts-1", "voice_id": "Priya", "accent": ""},
            {"id": "5e997567-1e3e-4f75-8744-721de533fe2c", "provider": "azuretts", "name": "Sonia", "model": "neural", "voice_id": "en-GB-SoniaNeural", "accent": "English (United Kingdom)"},
            {"id": "621917d6-5cac-4295-8d9f-17c26f50ec65", "provider": "smallest", "name": "Vidya", "model": "lightning-v2", "voice_id": "vidya", "accent": "Indian female kannada"},
            {"id": "6252156f-9bb9-435e-81e0-b014026d92d5", "provider": "inworld", "name": "Johanna", "model": "inworld-tts-1", "voice_id": "Johanna", "accent": ""},
            {"id": "67fa191c-88d2-4128-8c3d-49119de73c90", "provider": "elevenlabs", "name": "Vikram", "model": "eleven_turbo_v2_5", "voice_id": "7Q6qcYvsTRgb4IVcoAdK", "accent": "indian"},
            {"id": "68acd78f-8eb8-4184-ac74-692906f8939f", "provider": "inworld", "name": "Yichen", "model": "inworld-tts-1", "voice_id": "Yichen", "accent": ""},
            {"id": "6a7e1e6c-60df-41ec-8cab-6d5d241162ee", "provider": "smallest", "name": "Biswa", "model": "lightning-v2", "voice_id": "biswa", "accent": "Indian male bengali"},
            {"id": "6acc4579-84dd-4bf9-9364-b74649079913", "provider": "smallest", "name": "Gargi", "model": "lightning-v2", "voice_id": "gargi", "accent": "Indian female gujarati"},
            {"id": "6ad56300-295c-4bb0-8288-2c47987f60bf", "provider": "inworld", "name": "Gianni", "model": "inworld-tts-1", "voice_id": "Gianni", "accent": ""},
            {"id": "6b14d785-4d24-4974-8236-3b5f46d0870e", "provider": "sarvam", "name": "Anushka", "model": "bulbul:v2", "voice_id": "anushka", "accent": "Indian female punjabi"},
            {"id": "6ecf97ee-a12a-4054-8bc3-4a6ea7a7dae7", "provider": "sarvam", "name": "Karun", "model": "bulbul:v2", "voice_id": "karun", "accent": "Indian Male"},
            {"id": "711f570e-b2c2-4833-96d5-c9eae12e1f3e", "provider": "rime", "name": "Abbie", "model": "mistv2", "voice_id": "abbie", "accent": "Young Female US"},
            {"id": "73cd0e36-217f-4b1f-a3a5-4cc1063647df", "provider": "inworld", "name": "Wendy", "model": "inworld-tts-1", "voice_id": "Wendy", "accent": ""},
            {"id": "73f2ad2b-eb5a-4724-9b7b-c4fe03e783c6", "provider": "inworld", "name": "Edward", "model": "inworld-tts-1", "voice_id": "Edward", "accent": ""},
            {"id": "755b5a0f-1c62-451a-976e-355c9f28761f", "provider": "inworld", "name": "Timothy", "model": "inworld-tts-1", "voice_id": "Timothy", "accent": ""},
            {"id": "767ad9da-dca9-4403-aaaa-8d614f1284c6", "provider": "sarvam", "name": "Vidya", "model": "bulbul:v2", "voice_id": "vidya", "accent": "Indian Female Malayalam"},
            {"id": "76e5ec0d-62ee-4f7e-bfaf-bc47823ba5b4", "provider": "inworld", "name": "Katrien", "model": "inworld-tts-1", "voice_id": "Katrien", "accent": ""},
            {"id": "775f6423-6c4f-4834-9940-3f7b5f07baa8", "provider": "rime", "name": "Rodney", "model": "mistv2", "voice_id": "rodney", "accent": "Elder Male US"},
            {"id": "7ae44ce0-1841-4648-84ef-daf723e086dc", "provider": "sarvam", "name": "Karun", "model": "bulbul:v2", "voice_id": "karun", "accent": "Indian Male Malayalam"},
            {"id": "7d9fcc64-5f33-41c5-85b7-0cb3c2508649", "provider": "sarvam", "name": "Vidya", "model": "bulbul:v2", "voice_id": "vidya", "accent": "Indian female marathi"},
            {"id": "7fa291fc-6519-414b-bea2-cc9b28817d8c", "provider": "sarvam", "name": "Anushka", "model": "bulbul:v2", "voice_id": "anushka", "accent": "Indian female telugu"},
            {"id": "7fcc7cb5-b70e-43c4-ab6e-9fe80adb3362", "provider": "elevenlabs", "name": "George", "model": "eleven_turbo_v2_5", "voice_id": "JBFqnCBsd6RMkjVDRZzb", "accent": "british"},
            {"id": "81c3c333-53e7-41b0-96b9-e54b75b134fe", "provider": "smallest", "name": "Karan", "model": "lightning-v2", "voice_id": "karan", "accent": "Indian male marathi"},
            {"id": "83497cd8-baf1-478c-a91f-bd441e3525bb", "provider": "inworld", "name": "Craig", "model": "inworld-tts-1", "voice_id": "Craig", "accent": ""},
            {"id": "839cf764-81cf-4435-b269-3f4adcbbe211", "provider": "rime", "name": "Marta", "model": "mistv2", "voice_id": "marta", "accent": "Elder Female US"},
            {"id": "85448a73-bb3f-49c8-86aa-cd2f0c6d0c11", "provider": "sarvam", "name": "Karun", "model": "bulbul:v2", "voice_id": "karun", "accent": "Indian male bengali"},
            {"id": "87bc089b-178f-4d17-8857-443b7a2c7a0d", "provider": "inworld", "name": "Rafael", "model": "inworld-tts-1", "voice_id": "Rafael", "accent": ""},
            {"id": "8a4f881e-c784-4347-acba-87acffbb5e8d", "provider": "sarvam", "name": "Vidya", "model": "bulbul:v2", "voice_id": "vidya", "accent": "Indian female english"},
            {"id": "8ad47602-d02e-45bf-9b9c-ff5d4fd7b01b", "provider": "inworld", "name": "Josef", "model": "inworld-tts-1", "voice_id": "Josef", "accent": ""},
            {"id": "8ca85fde-526d-447a-9e2b-2d69fc7ea0be", "provider": "sarvam", "name": "Arya", "model": "bulbul:v2", "voice_id": "arya", "accent": "Indian Female Kannada"},
            {"id": "8cca6041-1bff-44fd-8edc-9e709c10517b", "provider": "inworld", "name": "Theodore", "model": "inworld-tts-1", "voice_id": "Theodore", "accent": ""},
            {"id": "8f1ee4c5-1681-4234-ae63-959502329bfe", "provider": "sarvam", "name": "Vidya", "model": "bulbul:v2", "voice_id": "vidya", "accent": "Indian Female Tamil"},
            {"id": "90cf00c3-7173-406f-989d-94886ca5c09c", "provider": "inworld", "name": "Hélène", "model": "inworld-tts-1", "voice_id": "Hélène", "accent": ""},
            {"id": "90d236d5-cd04-401f-abdd-5e589e1b5e77", "provider": "sarvam", "name": "Karun", "model": "bulbul:v2", "voice_id": "karun", "accent": "Indian male gujarati"},
            {"id": "9135a907-e481-4e2f-861f-96fe000ad644", "provider": "sarvam", "name": "Anushka", "model": "bulbul:v2", "voice_id": "anushka", "accent": "Indian Female Tamil"},
            {"id": "9237333b-5551-4463-81f0-e18d54d35a73", "provider": "inworld", "name": "Mathieu", "model": "inworld-tts-1", "voice_id": "Mathieu", "accent": ""},
            {"id": "9256589f-7815-40f5-8f3b-98eb858ddfea", "provider": "inworld", "name": "Wojciech", "model": "inworld-tts-1", "voice_id": "Wojciech", "accent": ""},
            {"id": "938931f3-f66b-40fc-b194-552bc32bf135", "provider": "elevenlabs", "name": "Monika Sogam", "model": "eleven_turbo_v2_5", "voice_id": "2zRM7PkgwBPiau2jvVXc", "accent": "indian"},
            {"id": "93d04790-0e76-4696-b30f-10a80078b698", "provider": "sarvam", "name": "Karun", "model": "bulbul:v2", "voice_id": "karun", "accent": "Indian Male Kannada"},
            {"id": "98549462-5f0f-4730-a909-9b5ab14877fe", "provider": "sarvam", "name": "Hitesh", "model": "bulbul:v2", "voice_id": "hitesh", "accent": "Indian male telugu"},
            {"id": "98cef306-9e1c-4923-9810-893c008444f2", "provider": "sarvam", "name": "Anushka", "model": "bulbul:v2", "voice_id": "anushka", "accent": "Indian Female"},
            {"id": "992614cf-b8ee-4a29-b646-3e77fd8f7cd0", "provider": "sarvam", "name": "Karun", "model": "bulbul:v2", "voice_id": "karun", "accent": "Indian male punjabi"},
            {"id": "99938325-fc2c-4b1a-83c1-f2728a11880e", "provider": "inworld", "name": "Minji", "model": "inworld-tts-1", "voice_id": "Minji", "accent": ""},
            {"id": "9c077b83-4167-4a37-a9d5-2fecf6785101", "provider": "inworld", "name": "Hyunwoo", "model": "inworld-tts-1", "voice_id": "Hyunwoo", "accent": ""},
            {"id": "a0fc3f45-3d58-4854-904e-aa0025f58cbc", "provider": "rime", "name": "Pola", "model": "arcana", "voice_id": "pola", "accent": "Middle Female US"},
            {"id": "a1003c26-6487-4ad8-8a75-8a033489c4e8", "provider": "inworld", "name": "Seojun", "model": "inworld-tts-1", "voice_id": "Seojun", "accent": ""},
            {"id": "a30482f0-cd4f-40c7-870f-6192a1fe9941", "provider": "rime", "name": "Gerald", "model": "mistv2", "voice_id": "gerald", "accent": "Young Male US"},
            {"id": "a3801785-539e-40d2-bf1d-9bac211fa2e2", "provider": "inworld", "name": "Erik", "model": "inworld-tts-1", "voice_id": "Erik", "accent": ""},
            {"id": "a42934c1-69e0-4b62-aaff-add8552dbc77", "provider": "sarvam", "name": "Arya", "model": "bulbul:v2", "voice_id": "arya", "accent": "Indian female english"},
            {"id": "a60dc6a9-ff38-4a58-a99b-e7dba01c23e6", "provider": "inworld", "name": "Orietta", "model": "inworld-tts-1", "voice_id": "Orietta", "accent": ""},
            {"id": "a767d56d-2ba9-4485-805c-2fb7d458ad47", "provider": "sarvam", "name": "Manisha", "model": "bulbul:v2", "voice_id": "manisha", "accent": "Indian female marathi"},
            {"id": "a784c9a9-bcee-424b-a707-9547818d45b0", "provider": "rime", "name": "Ursa", "model": "arcana", "voice_id": "ursa", "accent": "Young Male US"},
            {"id": "a7ff5e02-bbe4-4e55-a1fd-48666b345117", "provider": "inworld", "name": "Lore", "model": "inworld-tts-1", "voice_id": "Lore", "accent": ""},
            {"id": "a9c40420-1836-4ddf-aa46-b7223d6c52de", "provider": "sarvam", "name": "Hitesh", "model": "bulbul:v2", "voice_id": "hitesh", "accent": "Indian male marathi"},
            {"id": "ac2bf9e3-84e9-43fa-be9a-cedf70fb8f43", "provider": "sarvam", "name": "Abhilash", "model": "bulbul:v2", "voice_id": "abhilash", "accent": "Indian male marathi"},
            {"id": "acae8d06-2dda-46ba-b438-cf2bbd3be006", "provider": "inworld", "name": "Dennis", "model": "inworld-tts-1", "voice_id": "Dennis", "accent": ""},
            {"id": "b1e7dbcf-12b3-4b09-8afb-07db34ed39bd", "provider": "sarvam", "name": "Vidya", "model": "bulbul:v2", "voice_id": "vidya", "accent": "Indian female gujarati"},
            {"id": "b20394f5-ecde-4ce9-bd09-2c0d85b2a100", "provider": "elevenlabs", "name": "Otto", "model": "eleven_turbo_v2_5", "voice_id": "FTNCalFNG5bRnkkaP5Ug", "accent": "german"},
            {"id": "b29b4796-026e-47e1-afb5-ba9e2c618202", "provider": "sarvam", "name": "Manisha", "model": "bulbul:v2", "voice_id": "manisha", "accent": "Indian female telugu"},
            {"id": "b4374940-88ea-483a-aecd-67cf08fb8ae4", "provider": "sarvam", "name": "Manisha", "model": "bulbul:v2", "voice_id": "manisha", "accent": "Indian Female Malayalam"},
            {"id": "b5e451e9-5970-4188-b61e-1acb8f5ef2fe", "provider": "inworld", "name": "Asuka", "model": "inworld-tts-1", "voice_id": "Asuka", "accent": ""},
            {"id": "b9c95fb5-92e8-4682-ac5b-d1c50bda44f5", "provider": "inworld", "name": "Elizabeth", "model": "inworld-tts-1", "voice_id": "Elizabeth", "accent": ""},
            {"id": "bd4de2f4-72f5-4887-9e2b-1f813ac1c625", "provider": "sarvam", "name": "Anushka", "model": "bulbul:v2", "voice_id": "anushka", "accent": "Indian female english"},
            {"id": "bd8c1151-9a1a-41c3-8d60-c097c2ab6891", "provider": "inworld", "name": "Xiaoyin", "model": "inworld-tts-1", "voice_id": "Xiaoyin", "accent": ""},
            {"id": "bdac3bd6-fac7-43d0-881d-e99221b05f46", "provider": "sarvam", "name": "Vidya", "model": "bulbul:v2", "voice_id": "vidya", "accent": "Indian Female"},
            {"id": "bf34a5b0-67e9-413a-b5d8-fafb21665573", "provider": "elevenlabs", "name": "Ziina - Confident & Clear", "model": "eleven_turbo_v2_5", "voice_id": "FaqthkZu1EWxXxUFbAfb", "accent": "Middle Aged Female Indian"},
            {"id": "c17e4b13-20fb-4397-b6e0-841ebaf1af35", "provider": "inworld", "name": "Mark", "model": "inworld-tts-1", "voice_id": "Mark", "accent": ""},
            {"id": "c1ebdf17-e006-4e3c-9d45-d855a43d16e0", "provider": "sarvam", "name": "Abhilash", "model": "bulbul:v2", "voice_id": "abhilash", "accent": "Indian male telugu"},
            {"id": "c20361d7-a3e2-43f5-9f2f-d2929f608739", "provider": "sarvam", "name": "Anushka", "model": "bulbul:v2", "voice_id": "anushka", "accent": "Indian Female Kannada"},
            {"id": "c2342402-68f1-4cda-95bf-542804341ee6", "provider": "inworld", "name": "Dominus", "model": "inworld-tts-1", "voice_id": "Dominus", "accent": ""},
            {"id": "c24f74f5-c203-47d3-9787-f230f82c2b4f", "provider": "rime", "name": "Esther", "model": "arcana", "voice_id": "esther", "accent": "Older Female US"},
            {"id": "c2b9e83c-5c04-4205-940c-bcbc95d41532", "provider": "inworld", "name": "Pixie", "model": "inworld-tts-1", "voice_id": "Pixie", "accent": ""},
            {"id": "c803ea48-0fa3-453d-9bad-59f272f4075e", "provider": "inworld", "name": "Alain", "model": "inworld-tts-1", "voice_id": "Alain", "accent": ""},
            {"id": "c8ec8cd4-7cc1-4d14-a639-a6388a8c8f99", "provider": "sarvam", "name": "Manisha", "model": "bulbul:v2", "voice_id": "manisha", "accent": "Indian Female"},
            {"id": "d1320954-a69d-4ae7-8d61-9bed1474a6f2", "provider": "sarvam", "name": "Anushka", "model": "bulbul:v2", "voice_id": "anushka", "accent": "Indian female marathi"},
            {"id": "d1941989-5869-468c-9320-655e82d7474b", "provider": "inworld", "name": "Lupita", "model": "inworld-tts-1", "voice_id": "Lupita", "accent": ""},
            {"id": "d50252ba-c8fb-4015-b01f-2fc154fb7134", "provider": "sarvam", "name": "Hitesh", "model": "bulbul:v2", "voice_id": "hitesh", "accent": "Indian Male Tamil"},
            {"id": "d6969181-7dbf-4946-bfcf-66b286f741ff", "provider": "sarvam", "name": "Arya", "model": "bulbul:v2", "voice_id": "arya", "accent": "Indian Female"},
            {"id": "d7c812b2-ddb9-407e-92ad-37d3b8f4b909", "provider": "inworld", "name": "Alex", "model": "inworld-tts-1", "voice_id": "Alex", "accent": ""},
            {"id": "dae17000-c29b-453b-b460-6a8c5d170a03", "provider": "smallest", "name": "Vijay", "model": "lightning-v2", "voice_id": "vijay", "accent": "Indian male tamil"},
            {"id": "dca64aab-5f75-45d8-9e04-dee563cb8468", "provider": "sarvam", "name": "Vidya", "model": "bulbul:v2", "voice_id": "vidya", "accent": "Indian Female Kannada"},
            {"id": "dcb7904d-ef25-4984-923f-2e34f55aa943", "provider": "sarvam", "name": "Arya", "model": "bulbul:v2", "voice_id": "arya", "accent": "Indian female punjabi"},
            {"id": "df0a05d8-4fa3-44d3-9717-9294ea2c8113", "provider": "sarvam", "name": "Abhilash", "model": "bulbul:v2", "voice_id": "abhilash", "accent": "Indian male gujarati"},
            {"id": "e0850288-1d7f-4afb-9b3e-3ec8f4c93875", "provider": "smallest", "name": "Aditi", "model": "lightning-v2", "voice_id": "aditi", "accent": "indian female english (united states)"},
            {"id": "e19868d9-fca6-472d-ac8c-3a0413dbb2ae", "provider": "sarvam", "name": "Karun", "model": "bulbul:v2", "voice_id": "karun", "accent": "Indian male marathi"},
            {"id": "e3527da8-421c-4dee-a9e3-0abe21e4a15e", "provider": "inworld", "name": "Maitê", "model": "inworld-tts-1", "voice_id": "Maitê", "accent": ""},
            {"id": "e64c7167-3f57-4ea1-94d4-9cb1ae16c55c", "provider": "polly", "name": "Matthew", "model": "generative", "voice_id": "Matthew", "accent": "United States (English)"},
            {"id": "e91bbab1-44ab-4fdf-ac9e-6d234e1e6849", "provider": "sarvam", "name": "Arya", "model": "bulbul:v2", "voice_id": "arya", "accent": "Indian female gujarati"},
            {"id": "ea5aabb7-2887-4753-a88c-a234e7a7b571", "provider": "sarvam", "name": "Abhilash", "model": "bulbul:v2", "voice_id": "abhilash", "accent": "Indian Male Kannada"},
            {"id": "ebdce6e6-bb03-495f-a2b2-7540730d21a0", "provider": "sarvam", "name": "Abhilash", "model": "bulbul:v2", "voice_id": "abhilash", "accent": "Indian Male Tamil"},
            {"id": "ecc2473e-e31e-4ed9-b50d-79b3fd436f36", "provider": "sarvam", "name": "Anushka", "model": "bulbul:v2", "voice_id": "anushka", "accent": "Indian Female Malayalam"},
            {"id": "ed6d7804-d32a-40be-aded-930fe0fec30c", "provider": "sarvam", "name": "Hitesh", "model": "bulbul:v2", "voice_id": "hitesh", "accent": "Indian male punjabi"},
            {"id": "ef10996a-4783-4e4a-9ece-88020e857b98", "provider": "sarvam", "name": "Vidya", "model": "bulbul:v2", "voice_id": "vidya", "accent": "Indian female punjabi"},
            {"id": "ef6cbb12-0b9e-410f-afae-83606dfc354c", "provider": "inworld", "name": "Heitor", "model": "inworld-tts-1", "voice_id": "Heitor", "accent": ""},
            {"id": "f1807439-aa75-4a14-a6a5-e4b92703075c", "provider": "rime", "name": "Marissa", "model": "mistv2", "voice_id": "marissa", "accent": "Young Female US"},
            {"id": "f387ef99-b45e-4d51-9bab-1c33b6a1cf61", "provider": "smallest", "name": "Vijay", "model": "lightning-v2", "voice_id": "vijay", "accent": "indian male marathi"},
            {"id": "f555ffb7-b13c-44d1-affd-288a449feb25", "provider": "inworld", "name": "Satoshi", "model": "inworld-tts-1", "voice_id": "Satoshi", "accent": ""},
            {"id": "f58731b5-f146-4c57-b26b-c7beb0dbd5f5", "provider": "inworld", "name": "Sarah", "model": "inworld-tts-1", "voice_id": "Sarah", "accent": ""},
            {"id": "fa4d7c64-44c1-40fc-a81e-b3e170f53ccd", "provider": "rime", "name": "Linda", "model": "mistv2", "voice_id": "linda", "accent": "Middle Female US"},
            {"id": "fbe6cbd9-c859-4071-a96f-e0994d1820f2", "provider": "inworld", "name": "Miguel", "model": "inworld-tts-1", "voice_id": "Miguel", "accent": ""},
            {"id": "fcd3729f-4c06-4d84-82bb-410cce8cfeb5", "provider": "sarvam", "name": "Arya", "model": "bulbul:v2", "voice_id": "arya", "accent": "Indian female marathi"},
            {"id": "fe8b118f-f62d-4d7f-ba4c-7b60312c1b67", "provider": "sarvam", "name": "Hitesh", "model": "bulbul:v2", "voice_id": "hitesh", "accent": "Indian male bengali"}
        ]
        
        for voice_data in voices_data:
            voice = Voice(
                id=voice_data["id"],
                voice_id=voice_data["voice_id"],
                provider=voice_data["provider"],
                name=voice_data["name"],
                model=voice_data["model"],
                accent=voice_data["accent"]
            )
            db.add(voice)
        
        db.commit()
        logger.info(f"Successfully seeded {len(voices_data)} voices")
        
    except Exception as e:
        logger.error(f"Error seeding voices: {e}")
        if db:
            db.rollback()
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    seed_all_voices()