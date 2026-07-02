from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from api.database import ChatHistory, ChatMessage, Interaction, AgentTrace


class ChatRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_chat_session(self, title: str) -> ChatHistory:
        chat_history_session = ChatHistory(chat_title=title)
        # injects the session once at construction and uses self.session throughout.
        self.session.add(chat_history_session)
        await self.session.flush()
        await self.session.commit()
        return chat_history_session

    async def add_message(
        self,
        chat_id: int,
        role: str,
        content: str,
        created_at: str,
    ) -> ChatMessage:
        msg = ChatMessage(
            role=role,
            content=content,
            created_at=created_at,
            chat_history_id_fk=chat_id,
        )
        self.session.add(msg)
        await self.session.flush()
        await self.session.commit()
        return msg

    async def get_chat_messages(self, chat_id: int):
        try:
            clean_chat_id = int(chat_id)
        except (ValueError, TypeError):
            return None
        stmt = (
            select(ChatHistory)
            .options(selectinload(ChatHistory.chat_messages))
            .where(ChatHistory.id == clean_chat_id)
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()


    async def get_chat_history(self):
        stmt = select(ChatHistory)
        res = await self.session.execute(stmt)
        return res.scalars().all()

class InteractionRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_interaction(self, chat_history_id: int, query: str, status: str, agent_mode: str) -> Interaction:
        interaction = Interaction(chat_history_id_fk=chat_history_id, query=query, status=status, agent_mode=agent_mode)
        self.session.add(interaction)
        await self.session.flush()
        await self.session.commit()
        return interaction

    async def get_interaction(self, interaction_id: int):
        stmt = select(Interaction).options(selectinload(Interaction.agent_traces)).where(Interaction.id == interaction_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_interactions(self, chat_history_id: int):
        stmt = select(Interaction).options(selectinload(Interaction.agent_traces)).where(Interaction.chat_history_id_fk == chat_history_id)
        res = await self.session.execute(stmt)
        return res.scalars().all()

class AgentTraceRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_agent_trace(self, interaction_id: int, step_type: str, name: str, inputs: dict, outputs: dict, thinking: bool) -> AgentTrace:
        agent_trace = AgentTrace(interaction_id_fk=interaction_id, step_type=step_type, name=name, inputs=inputs, outputs=outputs, thinking=thinking)
        self.session.add(agent_trace)
        await self.session.flush()
        await self.session.commit()
        return agent_trace

    async def get_agent_trace(self, agent_trace_id: int):
        stmt = select(AgentTrace).where(AgentTrace.id == agent_trace_id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_agent_traces(self, interaction_id: int):
        stmt = select(AgentTrace).where(AgentTrace.interaction_id_fk == interaction_id)
        res = await self.session.execute(stmt)
        return res.scalars().all()
